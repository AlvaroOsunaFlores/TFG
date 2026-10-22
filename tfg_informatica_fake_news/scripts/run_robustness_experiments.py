"""Run a separately versioned, grouped robustness protocol.

The existing baseline and its files are immutable inputs. This command writes only
under the dedicated robustness data, report, and model directories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from analysis_utils import predict_with_threshold_policy, resolve_prediction_policy

# A 32-bit prime keeps a*x+b below 2**64, so NumPy uint64 arithmetic is exact
# before modular reduction (unlike multiplying 61-bit values in uint64).
MINHASH_PRIME = np.uint64(4_294_967_291)


def project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def payload_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=_json_default).encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")
    temporary.replace(path)


def _json_default(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Tipo no serializable en artefactos experimentales: {type(value).__name__}")


def text_shingles(text: str, size: int) -> set[int]:
    tokens = str(text).split()
    if len(tokens) < size:
        # For short texts only exact matches count as duplicates.
        return {int.from_bytes(hashlib.blake2b(str(text).encode("utf-8"), digest_size=8).digest(), "little")}
    return {
        int.from_bytes(hashlib.blake2b(" ".join(tokens[i : i + size]).encode("utf-8"), digest_size=4).digest(), "little")
        for i in range(len(tokens) - size + 1)
    }


def minhash_signature(shingles: set[int], a: np.ndarray, b: np.ndarray) -> tuple[int, ...]:
    values = np.fromiter((value % int(MINHASH_PRIME) for value in shingles), dtype=np.uint64)
    minima = np.full(len(a), MINHASH_PRIME - np.uint64(1), dtype=np.uint64)
    # Batch over every shingle, not a prefix/sample of the document.
    for start in range(0, len(values), 512):
        hashed = (values[start : start + 512, None] * a + b) % MINHASH_PRIME
        minima = np.minimum(minima, hashed.min(axis=0))
    return tuple(int(value) for value in minima)


def lsh_candidates(signatures: list[tuple[int, ...]], bands: int = 32) -> set[tuple[int, int]]:
    if len(signatures) == 0:
        return set()
    rows, remainder = divmod(len(signatures[0]), bands)
    if remainder:
        raise ValueError("La longitud de firma debe ser divisible por el número de bandas")
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = defaultdict(list)
    candidates: set[tuple[int, int]] = set()
    for index, raw_signature in enumerate(signatures):
        signature = tuple(int(value) for value in raw_signature)
        for band in range(bands):
            key = band, signature[band * rows : (band + 1) * rows]
            for prior in buckets[key]:
                candidates.add((prior, index))
            buckets[key].append(index)
    return candidates


def connected_components(size: int, pairs: list[tuple[int, int]]) -> list[int]:
    parent = list(range(size))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    for left, right in pairs:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left
    return [find(index) for index in range(size)]


def prepare_derived_dataset(frame: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Deduplicate exact texts, group near duplicates, and exclude label conflicts.

    Exact duplicates keep the smallest source_id as a representative. Near duplicate
    rows remain individually available for CV but share one group, so they cannot
    cross a training/test boundary. The audit includes one row for every original.
    """
    frame = frame.copy().sort_values("source_id", kind="stable").reset_index(drop=True)
    text_column = config["text_column"]
    label_column = config["label_column"]
    required = {"source_id", "dataset_name", text_column, label_column}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas para preparar corpus: {sorted(missing)}")
    if frame["source_id"].duplicated().any():
        raise ValueError("source_id debe ser único antes de deduplicar textos")
    frame[label_column] = frame[label_column].astype(int)
    exact_groups = frame.groupby(text_column, sort=False, dropna=False)
    exact_map: dict[int, list[int]] = {}
    representatives: list[int] = []
    exact_conflict_count = 0
    for _text, group in exact_groups:
        indices = group.index.tolist()
        representative = min(indices, key=lambda idx: str(frame.at[idx, "source_id"]))
        conflict = group[label_column].nunique() > 1
        if conflict:
            exact_conflict_count += 1
        # Keep a representative even for contradictory exact duplicates. Their
        # labels must propagate through near-duplicate components before the
        # complete conflicting component is excluded.
        representatives.append(representative)
        exact_map[representative] = indices
    retained = frame.loc[representatives].copy().reset_index(drop=True)
    representative_originals = [exact_map[idx] for idx in representatives]

    # The same seeded 128 MinHash permutations are used for every record.
    permutations = int(config["minhash_permutations"])
    if permutations != 128 or int(config["lsh_bands"]) != 32:
        raise ValueError("El protocolo fijado requiere 128 permutaciones y 32 bandas")
    rng = np.random.default_rng(int(config["random_state"]))
    a = rng.integers(1, int(MINHASH_PRIME) - 1, size=permutations, dtype=np.uint64)
    b = rng.integers(0, int(MINHASH_PRIME) - 1, size=permutations, dtype=np.uint64)
    shingle_size = int(config["shingle_size"])
    batch_size = int(config["signature_batch_size"])
    signatures = np.empty((len(retained), permutations), dtype=np.uint32)
    texts = retained[text_column].astype(str).tolist()
    for batch_start in range(0, len(texts), batch_size):
        batch_end = min(batch_start + batch_size, len(texts))
        for index in range(batch_start, batch_end):
            signatures[index] = minhash_signature(text_shingles(texts[index], shingle_size), a, b)
    candidates = lsh_candidates(signatures, int(config["lsh_bands"]))
    accepted: list[tuple[int, int]] = []
    for left, right in sorted(candidates):
        left_shingles = text_shingles(texts[left], shingle_size)
        right_shingles = text_shingles(texts[right], shingle_size)
        union = len(left_shingles | right_shingles)
        similarity = len(left_shingles & right_shingles) / union if union else 1.0
        if similarity >= float(config["near_duplicate_jaccard"]):
            accepted.append((left, right))
    roots = connected_components(len(retained), accepted)
    root_representatives: dict[int, str] = {}
    for index, root in enumerate(roots):
        source_id = str(retained.at[index, "source_id"])
        root_representatives[root] = min(root_representatives.get(root, source_id), source_id)
    root_names = {root: f"g-{source_id}" for root, source_id in root_representatives.items()}
    group_ids = [root_names[root] for root in roots]
    retained["duplicate_group"] = group_ids
    if "label_name" in retained.columns:
        retained["historical_label_name"] = retained["label_name"]
        retained["label_name"] = retained[label_column].map({0: "no_fake", 1: "fake_news"})
    else:
        retained["label_name"] = retained[label_column].map({0: "no_fake", 1: "fake_news"})
    retained["group_sources"] = retained.index.map(lambda idx: json.dumps(sorted({str(frame.at[o, "dataset_name"]) for o in representative_originals[idx]}), ensure_ascii=False))
    retained["is_cross_source_group"] = retained["group_sources"].map(lambda value: len(json.loads(value)) > 1)

    # Propagate all original source names into the full connected component.
    members_by_root: dict[int, list[int]] = defaultdict(list)
    for idx, root in enumerate(roots):
        members_by_root[root].append(idx)
    group_sources: dict[int, set[str]] = {}
    group_labels: dict[int, set[int]] = {}
    for root, member_indices in members_by_root.items():
        group_sources[root] = {str(frame.at[o, "dataset_name"]) for idx in member_indices for o in representative_originals[idx]}
        group_labels[root] = {
            int(frame.at[original_idx, label_column])
            for idx in member_indices
            for original_idx in representative_originals[idx]
        }
    conflict_roots = {root for root, labels in group_labels.items() if len(labels) > 1}
    retained["group_sources"] = [json.dumps(sorted(group_sources[root]), ensure_ascii=False) for root in roots]
    retained["is_cross_source_group"] = [len(group_sources[root]) > 1 for root in roots]
    updated_audit: list[dict[str, Any]] = []
    for idx, retained_row in retained.iterrows():
        root = roots[idx]
        group_id = group_ids[idx]
        cross_source = len(group_sources[root]) > 1
        conflict = root in conflict_roots
        for original_idx in representative_originals[idx]:
            record = frame.loc[original_idx]
            is_rep = str(record["source_id"]) == str(retained_row["source_id"])
            updated_audit.append({
                "source_id": record["source_id"], "representative_source_id": retained_row["source_id"],
                "dataset_name": record["dataset_name"], "normalized_text": record[text_column], "label": int(record[label_column]),
                "original_label_name": record.get("label_name", ""),
                "status": "excluded_conflicting_duplicate_group" if conflict else ("retained_representative" if is_rep else "deduplicated_exact"),
                "duplicate_group": group_id, "group_sources": json.dumps(sorted(group_sources[root]), ensure_ascii=False),
                "reason": "conflicting_labels" if conflict else ("exact_normalized_text" if not is_rep else ("cross_source_group" if cross_source else "")),
            })
    conflict_rows = retained.index[[root in conflict_roots for root in roots]].tolist()
    conflict_originals = {str(frame.at[o, "source_id"]) for idx in conflict_rows for o in representative_originals[idx]}
    final = retained.loc[[root not in conflict_roots for root in roots]].copy().reset_index(drop=True)
    audit = pd.DataFrame(updated_audit)
    metadata = {
        "source_rows": int(len(frame)), "derived_rows": int(len(final)),
        "exact_duplicate_rows_collapsed": int(len(frame) - len(representatives)),
        "exact_conflicting_groups_excluded": int(exact_conflict_count),
        "exact_conflicting_rows_excluded": int(sum(len(exact_map[idx]) for idx in representatives if frame.loc[exact_map[idx], label_column].nunique() > 1)),
        "near_duplicate_groups": int(sum(len(items) > 1 for items in members_by_root.values())),
        "near_duplicate_edges_confirmed": int(len(accepted)),
        "conflicting_groups_excluded": int(len(conflict_roots)),
        "conflicting_rows_excluded": int(len(conflict_originals)),
        "cross_source_groups": int(sum(len(sources) > 1 for sources in group_sources.values())),
        "cross_source_rows_excluded_from_transfer": int(sum(1 for _, row in final.iterrows() if row["is_cross_source_group"])),
        "minhash_permutations": permutations, "random_state": int(config["random_state"]), "lsh_bands": int(config["lsh_bands"]),
        "shingle_size": shingle_size, "signature_batch_size": batch_size, "near_duplicate_jaccard": float(config["near_duplicate_jaccard"]),
        "candidate_pairs": int(len(candidates)),
        "caveat": "MinHash LSH is an approximate candidate search and may miss paraphrases or near duplicates that share no LSH band.",
    }
    return final, audit, metadata


def build_pipeline(spec: dict[str, Any], random_state: int) -> Pipeline:
    tfidf = spec["tfidf"]
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=tuple(tfidf["ngram_range"]), min_df=int(tfidf["min_df"]), max_features=tfidf["max_features"])
    params = dict(spec["params"])
    if spec["classifier"] == "logistic_regression":
        classifier = LogisticRegression(random_state=random_state, solver=spec["solver"], **params)
    elif spec["classifier"] == "linear_svc":
        classifier = LinearSVC(random_state=random_state, dual=True, **params)
    else:
        raise ValueError(f"Clasificador no permitido: {spec['classifier']}")
    return Pipeline([("tfidf", vectorizer), ("classifier", classifier)])


def metric_payload(y_true: pd.Series, predictions: list[int]) -> dict[str, float]:
    return {"accuracy": float(accuracy_score(y_true, predictions)), "precision_macro": float(precision_score(y_true, predictions, average="macro", zero_division=0)), "recall_macro": float(recall_score(y_true, predictions, average="macro", zero_division=0)), "macro_f1": float(f1_score(y_true, predictions, average="macro", zero_division=0))}


def file_set_hash(paths: list[Path]) -> str:
    return payload_sha256({str(path.name): file_sha256(path) for path in paths})


def run_cross_validation(frame: pd.DataFrame, config: dict[str, Any], run_dir: Path, models_dir: Path, state: dict[str, Any], *, resume: bool) -> dict[str, Any]:
    policy = resolve_prediction_policy(config["prediction_policy"])
    splitter = StratifiedGroupKFold(n_splits=int(config["n_splits"]), shuffle=True, random_state=int(config["random_state"]))
    splits = list(splitter.split(frame, frame[config["label_column"]].astype(int), frame["duplicate_group"]))
    assignments = np.full(len(frame), -1, dtype=int)
    for fold, (_train, test) in enumerate(splits, start=1):
        assignments[test] = fold
    if (assignments < 1).any():
        raise RuntimeError("La validación cruzada no produjo predicción fuera de entrenamiento para todas las filas")
    if any(set(frame.iloc[train]["duplicate_group"]) & set(frame.iloc[test]["duplicate_group"]) for train, test in splits):
        raise RuntimeError("Un grupo de duplicados aparece simultáneamente en entrenamiento y prueba")
    assignment_path = run_dir / "fold_assignments.csv"
    assignment_frame = frame[["source_id", "dataset_name", "duplicate_group", config["label_column"]]].copy()
    assignment_frame["fold"] = assignments
    assignment_frame.to_csv(assignment_path, index=False)
    state["fold_assignments_sha256"] = file_sha256(assignment_path)
    atomic_json(run_dir / "run_state.json", state)

    result: dict[str, Any] = {"models": {}}
    for spec in config["candidate_models"]:
        name = spec["name"]
        model_dir = models_dir / name
        model_dir.mkdir(parents=True, exist_ok=True)
        fold_metrics = []
        prediction_frames = []
        for fold, (train_index, test_index) in enumerate(splits, start=1):
            pred_path = run_dir / f"{name}_fold_{fold}_predictions.csv"
            model_path = model_dir / f"fold_{fold}.joblib"
            checkpoint_path = run_dir / f"{name}_fold_{fold}.json"
            cached = resume and all(path.is_file() for path in [pred_path, model_path, checkpoint_path])
            if cached:
                checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                cached = (checkpoint.get("predictions_sha256") == file_sha256(pred_path)
                          and checkpoint.get("model_sha256") == file_sha256(model_path)
                          and state.get("completed_folds", {}).get(f"{name}:{fold}") == payload_sha256(checkpoint["metrics"]))
            if cached:
                pred_frame = pd.read_csv(pred_path)
                fold_payload = checkpoint["metrics"]
            else:
                print(f"Ajuste CV: {name}, fold {fold}/{config['n_splits']}...", flush=True)
                train, test = frame.iloc[train_index], frame.iloc[test_index]
                pipeline = build_pipeline(spec, int(config["random_state"]))
                start = time.perf_counter()
                caught: list[str] = []
                with warnings.catch_warnings(record=True) as observed:
                    warnings.simplefilter("always")
                    pipeline.fit(train[config["text_column"]].astype(str), train[config["label_column"]].astype(int))
                    caught = [str(item.message) for item in observed]
                elapsed = time.perf_counter() - start
                predictions, scores, score_kind, threshold = predict_with_threshold_policy(pipeline, test[config["text_column"]], prediction_policy=policy)
                pred_frame = test[["source_id", "dataset_name", config["label_column"], "duplicate_group"]].copy()
                pred_frame["fold"] = fold; pred_frame["pred"] = predictions; pred_frame["score"] = scores; pred_frame["score_kind"] = score_kind; pred_frame["threshold"] = threshold
                pred_frame.to_csv(pred_path, index=False)
                joblib.dump(pipeline, model_path)
                classifier = pipeline.named_steps["classifier"]
                fold_payload = {"fold": fold, "train_rows": int(len(train)), "test_rows": int(len(test)), "metrics": metric_payload(test[config["label_column"]].astype(int), predictions), "score_kind": score_kind, "threshold": threshold, "duration_seconds": elapsed, "n_iter": getattr(classifier, "n_iter_", None), "warnings": caught, "solver": ({"name": classifier.solver} if isinstance(classifier, LogisticRegression) else {"name": "liblinear", "dual": classifier.dual, "tol": classifier.tol, "max_iter": classifier.max_iter})}
                atomic_json(checkpoint_path, {"metrics": fold_payload, "predictions_sha256": file_sha256(pred_path), "model_sha256": file_sha256(model_path)})
                state.setdefault("completed_folds", {})[f"{name}:{fold}"] = payload_sha256(fold_payload)
                atomic_json(run_dir / "run_state.json", state)
            fold_metrics.append(fold_payload)
            prediction_frames.append(pred_frame)
        predictions_frame = pd.concat(prediction_frames, ignore_index=True).sort_values("source_id")
        pred_all_path = run_dir / f"{name}_oof_predictions.csv"
        predictions_frame.to_csv(pred_all_path, index=False)
        per_source = {source: {"metrics": metric_payload(group[config["label_column"]].astype(int), group["pred"].astype(int).tolist()), "confusion_matrix": confusion_matrix(group[config["label_column"]], group["pred"], labels=[0, 1]).tolist()} for source, group in predictions_frame.groupby("dataset_name")}
        metric_names = list(fold_metrics[0]["metrics"])
        means = {key: float(np.mean([item["metrics"][key] for item in fold_metrics])) for key in metric_names}
        stds = {key: float(np.std([item["metrics"][key] for item in fold_metrics], ddof=1)) for key in metric_names}
        matrix = confusion_matrix(predictions_frame[config["label_column"]], predictions_frame["pred"], labels=[0, 1]).tolist()
        result["models"][name] = {"folds": fold_metrics, "mean": means, "sample_std": stds, "global": metric_payload(predictions_frame[config["label_column"]].astype(int), predictions_frame["pred"].astype(int).tolist()), "confusion_matrix": matrix, "by_source": per_source, "oof_predictions_sha256": file_sha256(pred_all_path)}
    return result


def run_transfer(frame: pd.DataFrame, config: dict[str, Any], run_dir: Path, models_dir: Path, state: dict[str, Any], *, resume: bool) -> dict[str, Any]:
    policy = resolve_prediction_policy(config["prediction_policy"])
    output: dict[str, Any] = {}
    sources = sorted(frame["dataset_name"].unique())
    pairs = [(sources[0], sources[1]), (sources[1], sources[0])]
    for train_source, test_source in pairs:
        key = f"{train_source}_to_{test_source}"; output[key] = {}
        train = frame.loc[frame["dataset_name"].eq(train_source) & ~frame["is_cross_source_group"]]
        test = frame.loc[frame["dataset_name"].eq(test_source) & ~frame["is_cross_source_group"]]
        if set(train["duplicate_group"]) & set(test["duplicate_group"]):
            raise RuntimeError("Los grupos compartidos entre fuentes deben excluirse íntegramente de transferencia")
        if train.empty or test.empty:
            raise RuntimeError(f"Transferencia vacía: {key}")
        for spec in config["candidate_models"]:
            name = spec["name"]; stem = f"transfer_{train_source}_to_{test_source}_{name}"
            pred_path = run_dir / f"{stem}_predictions.csv"; model_path = models_dir / f"{stem}.joblib"; checkpoint_path = run_dir / f"{stem}.json"
            cached = resume and all(path.is_file() for path in [pred_path, model_path, checkpoint_path])
            if cached:
                checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                cached = (checkpoint.get("predictions_sha256") == file_sha256(pred_path)
                          and checkpoint.get("model_sha256") == file_sha256(model_path)
                          and state.get("completed_transfers", {}).get(stem) == payload_sha256(checkpoint["metrics"]))
            if cached:
                pred_frame = pd.read_csv(pred_path); payload = checkpoint["metrics"]
            else:
                print(f"Ajuste de transferencia: {key}, {name}...", flush=True)
                pipeline = build_pipeline(spec, int(config["random_state"]))
                caught: list[str] = []
                start = time.perf_counter()
                with warnings.catch_warnings(record=True) as observed:
                    warnings.simplefilter("always")
                    pipeline.fit(train[config["text_column"]].astype(str), train[config["label_column"]].astype(int))
                    caught = [str(item.message) for item in observed]
                elapsed = time.perf_counter() - start
                predictions, scores, score_kind, threshold = predict_with_threshold_policy(pipeline, test[config["text_column"]], prediction_policy=policy)
                pred_frame = test[["source_id", "dataset_name", config["label_column"], "duplicate_group"]].copy()
                pred_frame["pred"] = predictions; pred_frame["score"] = scores; pred_frame["score_kind"] = score_kind; pred_frame["threshold"] = threshold
                pred_frame.to_csv(pred_path, index=False); joblib.dump(pipeline, model_path)
                classifier = pipeline.named_steps["classifier"]
                payload = {"train_source": train_source, "test_source": test_source, "train_rows": int(len(train)), "test_rows": int(len(test)), "metrics": metric_payload(test[config["label_column"]].astype(int), predictions), "confusion_matrix": confusion_matrix(test[config["label_column"]], predictions, labels=[0, 1]).tolist(), "score_kind": score_kind, "threshold": threshold, "duration_seconds": elapsed, "n_iter": getattr(classifier, "n_iter_", None), "warnings": caught, "solver": ({"name": classifier.solver} if isinstance(classifier, LogisticRegression) else {"name": "liblinear", "dual": classifier.dual, "tol": classifier.tol, "max_iter": classifier.max_iter})}
                atomic_json(checkpoint_path, {"metrics": payload, "predictions_sha256": file_sha256(pred_path), "model_sha256": file_sha256(model_path)})
                state.setdefault("completed_transfers", {})[stem] = payload_sha256(payload); atomic_json(run_dir / "run_state.json", state)
            output[key][name] = payload
    return output


def validate_config(config: dict[str, Any]) -> None:
    required = {"source_dataset_path", "derived_dataset_dir", "reports_dir", "models_dir", "text_column", "label_column", "random_state", "n_splits", "minhash_permutations", "lsh_bands", "shingle_size", "signature_batch_size", "near_duplicate_jaccard", "prediction_policy", "candidate_models"}
    missing = required - set(config)
    if missing:
        raise ValueError(f"Configuración incompleta: {sorted(missing)}")
    if int(config["n_splits"]) != 5 or int(config["minhash_permutations"]) != 128 or int(config["lsh_bands"]) != 32 or int(config["shingle_size"]) != 5 or float(config["near_duplicate_jaccard"]) != 0.9:
        raise ValueError("La configuración no coincide con el protocolo de robustez fijado")
    if int(config["signature_batch_size"]) < 1 or int(config["random_state"]) != 42:
        raise ValueError("signature_batch_size debe ser positivo y random_state debe ser 42")
    names = {model.get("name") for model in config["candidate_models"]}
    logistic = next((model for model in config["candidate_models"] if model.get("name") == "logistic_regression"), {})
    if logistic.get("solver") != "lbfgs":
        raise ValueError("logistic_regression must explicitly use solver=lbfgs")
    if names != {"logistic_regression", "linear_svc"}:
        raise ValueError("Se requieren exactamente regresión logística y LinearSVC")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/robustness_config.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", metavar="RUN_ID")
    args = parser.parse_args()
    config_path = project_path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8")); validate_config(config)
    source_path = project_path(config["source_dataset_path"])
    source_hash, config_hash, code_hash = file_sha256(source_path), file_sha256(config_path), file_sha256(Path(__file__))
    versions = {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__}
    identity = payload_sha256({"source": source_hash, "config": config_hash, "code": code_hash, "versions": versions})
    if args.dry_run:
        print(json.dumps({"run_id": f"robustness-{identity[:16]}", "source_sha256": source_hash, "config_sha256": config_hash, "code_sha256": code_hash, "protocol": {key: config[key] for key in ["n_splits", "random_state", "minhash_permutations", "lsh_bands", "shingle_size", "near_duplicate_jaccard"]}}, indent=2))
        return
    run_id = args.resume or f"robustness-{identity[:16]}"
    run_dir = project_path(config["reports_dir"]) / run_id
    models_dir = project_path(config["models_dir"]) / run_id
    derived_dir = project_path(config["derived_dataset_dir"]) / run_id
    if args.resume:
        state_path = run_dir / "run_state.json"
        if not state_path.is_file():
            raise FileNotFoundError("No existe estado recuperable para ese run_id")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        expected = {"identity_sha256": identity, "source_sha256": source_hash, "config_sha256": config_hash, "code_sha256": code_hash, "versions": versions}
        if any(state.get(key) != value for key, value in expected.items()):
            raise ValueError("Los hashes o versiones no coinciden; no se reanudará una ejecución diferente")
    else:
        run_dir.mkdir(parents=True, exist_ok=False); models_dir.mkdir(parents=True, exist_ok=False); derived_dir.mkdir(parents=True, exist_ok=False)
        state = {"run_id": run_id, "identity_sha256": identity, "source_sha256": source_hash, "config_sha256": config_hash, "code_sha256": code_hash, "versions": versions, "status": "running", "started_at_utc": datetime.now(timezone.utc).isoformat(), "completed_folds": {}, "completed_transfers": {}}
        atomic_json(run_dir / "run_state.json", state)
        atomic_json(run_dir / "protocol.json", {"protocol_status": "fixed before this run; not a retrospective preregistration", "config": config, "identity_sha256": identity})
    derived_path, audit_path, preparation_path = derived_dir / "derived_corpus.csv.gz", derived_dir / "exclusion_audit.csv", run_dir / "preparation.json"
    prepared = args.resume and all(path.is_file() for path in [derived_path, audit_path, preparation_path])
    if prepared:
        preparation = json.loads(preparation_path.read_text(encoding="utf-8"))
        prepared = preparation.get("derived_sha256") == file_sha256(derived_path) and preparation.get("audit_sha256") == file_sha256(audit_path)
    if prepared:
        frame = pd.read_csv(derived_path, compression="gzip", keep_default_na=False)
        audit = pd.read_csv(audit_path, keep_default_na=False)
    else:
        print("Preparando corpus con MinHash sobre todos los shingles...", flush=True)
        source = pd.read_csv(source_path, compression="infer", keep_default_na=False)
        frame, audit, stats = prepare_derived_dataset(source, config)
        frame.to_csv(derived_path, index=False, compression="gzip"); audit.to_csv(audit_path, index=False)
        preparation = {**stats, "source_sha256": source_hash, "derived_sha256": file_sha256(derived_path), "audit_sha256": file_sha256(audit_path), "derived_rows": int(len(frame))}
        atomic_json(preparation_path, preparation)
    print(f"Corpus listo: {len(frame)} filas. Validación cruzada y transferencia...", flush=True)
    state.setdefault("stages", {})
    state["stages"]["preparation"] = {"status": "completed", "derived_sha256": preparation["derived_sha256"], "audit_sha256": preparation["audit_sha256"]}
    state["stages"]["cross_validation"] = {"status": "running"}
    atomic_json(run_dir / "run_state.json", state)
    cv = run_cross_validation(frame, config, run_dir, models_dir, state, resume=bool(args.resume))
    state["stages"]["cross_validation"] = {"status": "completed"}
    state["stages"]["transfer"] = {"status": "running"}
    atomic_json(run_dir / "run_state.json", state)
    transfer = run_transfer(frame, config, run_dir, models_dir, state, resume=bool(args.resume))
    state["stages"]["transfer"] = {"status": "completed"}
    svc_mean = cv["models"]["linear_svc"]["mean"]["macro_f1"]
    lr_mean = cv["models"]["logistic_regression"]["mean"]["macro_f1"]
    manifest = {"run_id": run_id, "identity_sha256": identity, "created_at_utc": state["started_at_utc"], "completed_at_utc": datetime.now(timezone.utc).isoformat(), "status": "completed", "source_sha256": source_hash, "config_sha256": config_hash, "code_sha256": code_hash, "versions": versions, "effective_config": config, "preparation": preparation, "cross_validation": cv, "transfer": transfer, "model_selected_by_mean_macro_f1": "linear_svc" if svc_mean > lr_mean else "logistic_regression", "comparison_caveat": "The five-fold mean is an internal model comparison, not an independent estimate after model selection."}
    atomic_json(run_dir / "robustness_manifest.json", manifest)
    state["status"] = "completed"; state["completed_at_utc"] = manifest["completed_at_utc"]; atomic_json(run_dir / "run_state.json", state)
    print(run_dir)


if __name__ == "__main__":
    main()
