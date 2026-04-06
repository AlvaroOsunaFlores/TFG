from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score

from experiment_registry import ensure_run_dir
from scripts.validate_dataset import load_dataset, validate_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "labeled" / "fake_news_unified.csv.gz"


def _resolve_project_path(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def compute_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evalua un baseline ya entrenado cuando exista un modelo persistido.")
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--dataset", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--outdir", default="reports/evaluations")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    with manifest_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> None:
    args = parse_args()
    manifest_payload: dict[str, Any] | None = None

    manifest_path = _resolve_project_path(args.manifest) if args.manifest else None
    if manifest_path and manifest_path.exists():
        manifest_payload = _load_manifest(manifest_path)

    dataset_path = _resolve_project_path(args.dataset or (manifest_payload or {}).get("dataset_path", DEFAULT_DATASET))
    raw_model_path = args.model or (manifest_payload or {}).get("model_path")
    model_path = _resolve_project_path(raw_model_path) if raw_model_path else None
    outdir = _resolve_project_path(args.outdir)

    if args.dry_run:
        payload = {
            "manifest": str(manifest_path) if manifest_path else None,
            "dataset_path": str(dataset_path),
            "dataset_exists": dataset_path.exists(),
            "model_path": str(model_path) if model_path else "",
            "model_exists": model_path.exists() if model_path else False,
            "outdir": str(outdir),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("OK dry-run: evaluacion preparada, sin inferencia ejecutada.")
        return

    if not model_path or not model_path.exists():
        raise SystemExit("Debes indicar un modelo entrenado valido o un manifest existente.")

    df = load_dataset(dataset_path)
    errors, _warnings = validate_dataframe(df)
    if errors:
        raise SystemExit("No se puede evaluar: el dataset no pasa la validacion previa.")

    text_column = (manifest_payload or {}).get("text_column", "normalized_text")
    label_column = (manifest_payload or {}).get("label_column", "label")

    model = joblib.load(model_path)
    predictions = model.predict(df[text_column].astype(str))

    metrics = compute_metrics(df[label_column].astype(int), predictions)
    report = classification_report(df[label_column].astype(int), predictions, output_dict=True, zero_division=0)

    _run_id, run_dir = ensure_run_dir(outdir, "evaluation")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    predictions_path = run_dir / f"evaluation_predictions_{stamp}.csv"
    pd.DataFrame(
        {
            "text": df[text_column],
            "label": df[label_column],
            "pred": predictions,
        }
    ).to_csv(predictions_path, index=False)

    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "metrics": metrics,
        "classification_report": report,
        "predictions_path": str(predictions_path),
    }
    summary_path = run_dir / f"evaluation_summary_{stamp}.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"OK evaluation -> {_display_path(summary_path)}")


if __name__ == "__main__":
    main()
