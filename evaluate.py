import os
import json
import time
import uuid
import hashlib
import platform
import pandas as pd

import torch
from model_loader import load_tokenizer_and_model

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
)


HF_MODEL = os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

INPUT_CSV = os.getenv("EVAL_INPUT", "data/test.csv")
OUT_DIR = os.getenv("EVAL_OUTDIR", "reports")
# Umbral por defecto orientado a recall alto para deteccion de amenazas.
THRESHOLD = float(os.getenv("THRESHOLD", "0.05"))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    run_id = str(uuid.uuid4())
    started_at = time.time()

    df = pd.read_csv(INPUT_CSV)
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)

    tokenizer, model, model_source = load_tokenizer_and_model(HF_MODEL, DEVICE)

    # Por defecto, usamos la clase 1 como positiva
    pos_id = 1

    y_true = df["label"].tolist()
    y_pred = []
    score_1 = []

    for text in df["text"].tolist():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=1)[0].tolist()

        p1 = float(probs[pos_id])
        score_1.append(p1)
        y_pred.append(1 if p1 >= THRESHOLD else 0)

    # Metricas agregadas
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

    # Barrido de umbrales para analisis de sensibilidad
    threshold_rows = []
    for t in [round(i / 100, 2) for i in range(5, 100, 5)]:
        preds_t = [1 if s >= t else 0 for s in score_1]
        threshold_rows.append(
            {
                "threshold": t,
                "precision_pos": float(precision_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "recall_pos": float(recall_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "f1_pos": float(f1_score(y_true, preds_t, pos_label=1, zero_division=0)),
                "accuracy": float(accuracy_score(y_true, preds_t)),
            }
        )

    threshold_df = pd.DataFrame(threshold_rows)
    best_row = threshold_df.sort_values(["f1_pos", "recall_pos"], ascending=False).iloc[0].to_dict()

    # predictions.csv
    out_pred = df.copy()
    out_pred["pred"] = y_pred
    out_pred["score_1"] = score_1
    out_pred["run_id"] = run_id
    out_pred["threshold_used"] = THRESHOLD
    out_pred["text_sha256"] = out_pred["text"].map(lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest())
    out_pred.to_csv(os.path.join(OUT_DIR, "predictions.csv"), index=False)
    threshold_df.to_csv(os.path.join(OUT_DIR, "threshold_analysis.csv"), index=False)

    # confusion_matrix.csv
    labels = [0, 1]
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    pd.DataFrame(cm, index=labels, columns=labels).to_csv(os.path.join(OUT_DIR, "confusion_matrix.csv"))

    # metrics.json (incluye trazabilidad mínima)
    report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

    payload = {
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": round(time.time() - started_at, 3),
        "hf_model": HF_MODEL,
        "model_source": model_source,
        "threshold": THRESHOLD,
        "input_csv": INPUT_CSV,
        "input_csv_sha256": sha256_file(INPUT_CSV),
        "num_samples": int(len(df)),
        "label_distribution": {str(k): int(v) for k, v in df["label"].value_counts().sort_index().items()},
        "labels": labels,
        "device": str(DEVICE),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "pandas_version": pd.__version__,
        "metrics": metrics,
        "best_threshold_by_f1": best_row,
        "classification_report": report,
    }

    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("OK -> reports/metrics.json, reports/confusion_matrix.csv, reports/predictions.csv, reports/threshold_analysis.csv")


if __name__ == "__main__":
    main()
