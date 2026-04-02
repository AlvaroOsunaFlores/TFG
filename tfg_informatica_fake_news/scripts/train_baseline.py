from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from experiment_registry import dataset_sha256, ensure_run_dir
from scripts.validate_dataset import validate_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "training_config.json"


def _resolve_project_path(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def load_training_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as fh:
        config = json.load(fh)

    config["dataset_path"] = _resolve_project_path(config["dataset_path"])
    config["reports_dir"] = _resolve_project_path(config["reports_dir"])

    model_output_dir = Path(config["model_output_dir"])
    if not model_output_dir.is_absolute():
        model_output_dir = PROJECT_ROOT / model_output_dir
    config["model_output_dir"] = model_output_dir
    return config


def build_pipeline(model_spec: dict[str, Any], random_state: int) -> Pipeline:
    tfidf_cfg = model_spec.get("tfidf", {})
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=tuple(tfidf_cfg.get("ngram_range", [1, 2])),
        min_df=int(tfidf_cfg.get("min_df", 1)),
        max_features=tfidf_cfg.get("max_features", 5000),
    )

    classifier_name = model_spec["classifier"]
    params = dict(model_spec.get("params", {}))

    if classifier_name == "logistic_regression":
        classifier = LogisticRegression(random_state=random_state, **params)
    elif classifier_name == "linear_svc":
        classifier = LinearSVC(random_state=random_state, **params)
    else:
        raise ValueError(f"Clasificador no soportado: {classifier_name}")

    return Pipeline(
        [
            ("tfidf", vectorizer),
            ("classifier", classifier),
        ]
    )


def compute_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entrena baselines de texto para fake news cuando exista un dataset real.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    config = load_training_config(config_path)
    if args.dataset:
        config["dataset_path"] = _resolve_project_path(args.dataset)

    dataset_path: Path = config["dataset_path"]
    df = pd.read_csv(dataset_path)
    errors, warnings = validate_dataframe(df)
    if errors:
        raise SystemExit("No se puede entrenar: el dataset no pasa la validacion previa.")

    text_column = config["text_column"]
    label_column = config["label_column"]

    plan_payload = {
        "config": str(config_path),
        "dataset_path": str(dataset_path),
        "rows": int(len(df)),
        "label_distribution": {str(key): int(value) for key, value in df[label_column].value_counts().sort_index().items()},
        "text_column": text_column,
        "reports_dir": str(config["reports_dir"]),
        "model_output_dir": str(config["model_output_dir"]),
        "candidates": [spec["name"] for spec in config["candidate_models"]],
        "warnings": warnings,
    }

    if args.dry_run:
        print(json.dumps(plan_payload, indent=2, ensure_ascii=False))
        print("OK dry-run: pipeline preparado, sin entrenamiento ejecutado.")
        return

    if len(df[label_column].unique()) < 2:
        raise SystemExit("No se puede entrenar con una sola clase.")

    X_train, X_test, y_train, y_test = train_test_split(
        df[text_column].astype(str),
        df[label_column].astype(int),
        test_size=float(config["test_size"]),
        random_state=int(config["random_state"]),
        stratify=df[label_column].astype(int),
    )

    run_id, run_dir = ensure_run_dir(config["reports_dir"], "baseline")
    _model_run_id, model_dir = ensure_run_dir(config["model_output_dir"], "baseline-model")

    comparison_rows: list[dict[str, Any]] = []
    best_payload: dict[str, Any] | None = None
    best_score = float("-inf")

    for model_spec in config["candidate_models"]:
        pipeline = build_pipeline(model_spec, int(config["random_state"]))
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        metrics = compute_metrics(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        comparison_rows.append({"name": model_spec["name"], **metrics})

        candidate_score = metrics[config["selection_metric"]]
        if candidate_score > best_score:
            best_score = candidate_score
            best_payload = {
                "spec": model_spec,
                "pipeline": pipeline,
                "metrics": metrics,
                "classification_report": report,
                "predictions": y_pred.tolist(),
            }

    if best_payload is None:
        raise SystemExit("No se ha podido seleccionar un baseline.")

    comparison_path = run_dir / "comparison.json"
    comparison_path.write_text(json.dumps(comparison_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    predictions_path = run_dir / "holdout_predictions.csv"
    pd.DataFrame(
        {
            "text": X_test.tolist(),
            "label": y_test.tolist(),
            "pred": best_payload["predictions"],
        }
    ).to_csv(predictions_path, index=False)

    report_path = run_dir / "classification_report.json"
    report_path.write_text(
        json.dumps(best_payload["classification_report"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    model_path = model_dir / "baseline_pipeline.joblib"
    joblib.dump(best_payload["pipeline"], model_path)

    manifest = {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset_sha256(dataset_path),
        "text_column": text_column,
        "label_column": label_column,
        "selection_metric": config["selection_metric"],
        "best_model": best_payload["spec"]["name"],
        "metrics": best_payload["metrics"],
        "model_path": str(model_path),
        "predictions_path": str(predictions_path),
        "report_path": str(report_path),
        "config_path": str(config_path),
    }
    manifest_path = run_dir / "training_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OK baseline -> {_display_path(manifest_path)}")


if __name__ == "__main__":
    main()
