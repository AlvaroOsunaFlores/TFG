from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import time
import uuid

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
import torch

from model_loader import load_tokenizer_and_model
from reporting import ensure_run_dir, mirror_latest_files, relative_report_path, write_json

PROJECT_ROOT = Path(__file__).resolve().parent


HF_MODEL = os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _project_path_from_env(name: str, default_relative: str) -> Path:
    raw = os.getenv(name, default_relative)
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


INPUT_CSV = _project_path_from_env("EVAL_INPUT", "data/test.csv")
REPORTS_DIR = _project_path_from_env("EVAL_OUTDIR", "reports")
THRESHOLD = float(os.getenv("THRESHOLD", "0.05"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    run_id = str(uuid.uuid4())
    run_dir = ensure_run_dir(REPORTS_DIR, run_id)
    started_at = time.time()

    df = pd.read_csv(INPUT_CSV)
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)

    tokenizer, model, model_source = load_tokenizer_and_model(HF_MODEL, DEVICE)
    pos_id = 1

    y_true = df["label"].tolist()
    y_pred: list[int] = []
    score_1: list[float] = []

    for text in df["text"].tolist():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1)[0].tolist()

        p1 = float(probs[pos_id])
        score_1.append(p1)
        y_pred.append(1 if p1 >= THRESHOLD else 0)

    try:
        roc_auc = float(roc_auc_score(y_true, score_1))
    except ValueError:
        roc_auc = None

    try:
        avg_precision = float(average_precision_score(y_true, score_1))
    except ValueError:
        avg_precision = None

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_pos": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "recall_pos": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "f1_pos": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "roc_auc": roc_auc,
        "average_precision": avg_precision,
    }

    threshold_rows = []
    for threshold in [round(value / 100, 2) for value in range(5, 100, 5)]:
        preds_t = [1 if score >= threshold else 0 for score in score_1]
        threshold_rows.append(
            {
                "threshold": threshold,
                "precision_pos": float(precision_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "recall_pos": float(recall_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "f1_pos": float(f1_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "accuracy": float(accuracy_score(y_true, preds_t)),
            }
        )

    threshold_df = pd.DataFrame(threshold_rows)
    best_row = threshold_df.sort_values(["f1_pos", "recall_pos"], ascending=False).iloc[0].to_dict()

    predictions_path = run_dir / "predictions.csv"
    out_pred = df.copy()
    out_pred["pred"] = y_pred
    out_pred["score_1"] = score_1
    out_pred["run_id"] = run_id
    out_pred["threshold_used"] = THRESHOLD
    out_pred["text_sha256"] = out_pred["text"].map(lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest())
    out_pred.to_csv(predictions_path, index=False)

    threshold_path = run_dir / "threshold_analysis.csv"
    threshold_df.to_csv(threshold_path, index=False)

    confusion_path = run_dir / "confusion_matrix.csv"
    labels = [0, 1]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    pd.DataFrame(matrix, index=labels, columns=labels).to_csv(confusion_path)

    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    metrics_path = run_dir / "metrics.json"
    payload = {
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round(time.time() - started_at, 3),
        "hf_model": HF_MODEL,
        "model_source": model_source,
        "threshold": THRESHOLD,
        "input_csv": str(INPUT_CSV.as_posix()),
        "input_csv_sha256": sha256_file(INPUT_CSV),
        "num_samples": int(len(df)),
        "label_distribution": {str(key): int(value) for key, value in df["label"].value_counts().sort_index().items()},
        "labels": labels,
        "device": str(DEVICE),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "pandas_version": pd.__version__,
        "metrics": metrics,
        "best_threshold_by_f1": best_row,
        "classification_report": report,
        "artifacts_dir": relative_report_path(run_dir, REPORTS_DIR),
        "artifacts": {
            "metrics": relative_report_path(metrics_path, REPORTS_DIR),
            "predictions": relative_report_path(predictions_path, REPORTS_DIR),
            "thresholds": relative_report_path(threshold_path, REPORTS_DIR),
            "confusion_matrix": relative_report_path(confusion_path, REPORTS_DIR),
        },
    }
    write_json(metrics_path, payload)

    mirror_latest_files(
        run_dir,
        REPORTS_DIR,
        ["metrics.json", "predictions.csv", "threshold_analysis.csv", "confusion_matrix.csv"],
    )

    print(
        "OK -> "
        f"{relative_report_path(metrics_path, REPORTS_DIR)}, "
        f"{relative_report_path(confusion_path, REPORTS_DIR)}, "
        f"{relative_report_path(predictions_path, REPORTS_DIR)}, "
        f"{relative_report_path(threshold_path, REPORTS_DIR)}"
    )


if __name__ == "__main__":
    main()
