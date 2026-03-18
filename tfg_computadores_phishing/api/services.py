from __future__ import annotations

import csv
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
from pymongo import MongoClient

from .settings import Settings


def _metrics_files(reports_dir: Path) -> list[Path]:
    files: list[Path] = []
    root_metrics = reports_dir / "metrics.json"
    if root_metrics.exists():
        files.append(root_metrics)

    runs_dir = reports_dir / "runs"
    if runs_dir.exists():
        for candidate in sorted(runs_dir.glob("*/metrics.json")):
            if candidate not in files:
                files.append(candidate)

    for candidate in sorted(reports_dir.glob("metrics_*.json")):
        if candidate not in files:
            files.append(candidate)
    return files


def _resolve_artifacts_dir(reports_dir: Path, payload: dict[str, Any], metrics_path: Path) -> Path:
    artifacts_dir = payload.get("artifacts_dir")
    if isinstance(artifacts_dir, str) and artifacts_dir.strip():
        return reports_dir / Path(artifacts_dir)
    if metrics_path.parent != reports_dir:
        return metrics_path.parent
    return reports_dir


def check_reports_available(reports_dir: Path) -> tuple[bool, str | None]:
    payloads = load_metrics_payloads(reports_dir)
    if not payloads:
        return False, "Missing report files: metrics.json"

    latest = payloads[0]
    artifacts_dir = Path(str(latest["_artifacts_dir"]))
    required = [
        artifacts_dir / "metrics.json",
        artifacts_dir / "threshold_analysis.csv",
        artifacts_dir / "confusion_matrix.csv",
    ]
    missing = [str(path.relative_to(reports_dir)) for path in required if not path.exists()]
    if missing:
        return False, f"Missing report files: {', '.join(missing)}"
    return True, None


def check_mongo_connection(settings: Settings) -> tuple[bool, str | None]:
    try:
        client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=1500)
        client.admin.command("ping")
        client.close()
        return True, None
    except Exception as exc:  # pragma: no cover - defensive for infra envs
        return False, str(exc)


def load_metrics_payloads(reports_dir: Path) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    seen_run_ids: set[str] = set()

    for file_path in _metrics_files(reports_dir):
        with file_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        run_id = str(payload.get("run_id", "")).strip()
        if not run_id or run_id in seen_run_ids:
            continue

        payload["_metrics_path"] = str(file_path)
        payload["_artifacts_dir"] = str(_resolve_artifacts_dir(reports_dir, payload, file_path))
        seen_run_ids.add(run_id)
        payloads.append(payload)

    payloads.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)
    return payloads


def get_run_payload_by_id(payloads: list[dict[str, Any]], run_id: str) -> dict[str, Any] | None:
    for payload in payloads:
        if str(payload.get("run_id")) == run_id:
            return payload
    return None


def run_summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": payload.get("run_id"),
        "timestamp": payload.get("timestamp"),
        "hf_model": payload.get("hf_model"),
        "model_source": payload.get("model_source"),
        "threshold": payload.get("threshold"),
        "num_samples": payload.get("num_samples"),
        "label_distribution": payload.get("label_distribution", {}),
        "metrics": payload.get("metrics", {}),
    }


def load_threshold_points(artifacts_dir: Path) -> list[dict[str, float]]:
    path = artifacts_dir / "threshold_analysis.csv"
    rows: list[dict[str, float]] = []

    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(
                {
                    "threshold": float(row["threshold"]),
                    "precision_pos": float(row["precision_pos"]),
                    "recall_pos": float(row["recall_pos"]),
                    "f1_pos": float(row["f1_pos"]),
                    "accuracy": float(row["accuracy"]),
                }
            )

    return rows


def load_confusion_payload(artifacts_dir: Path) -> dict[str, Any]:
    path = artifacts_dir / "confusion_matrix.csv"
    frame = pd.read_csv(path, index_col=0)

    labels = [int(col) for col in frame.columns.tolist()]
    matrix = [[int(value) for value in row] for row in frame.values.tolist()]

    normalized: list[list[float]] = []
    for row in matrix:
        total = sum(row)
        if total == 0:
            normalized.append([0.0 for _ in row])
        else:
            normalized.append([round(value / total, 6) for value in row])

    return {
        "labels": labels,
        "matrix": matrix,
        "normalized": normalized,
    }


def _serialize_datetime(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None:
        return None
    return str(value)


def fetch_messages(
    settings: Settings,
    *,
    run_id: str | None,
    pred: int | None,
    score_min: float | None,
    date_from: datetime | None,
    date_to: datetime | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    query: dict[str, Any] = {}
    if run_id:
        query["run_id"] = run_id
    if pred is not None:
        query["pred"] = pred
    if score_min is not None:
        query["score_1"] = {"$gte": score_min}

    created_filter: dict[str, datetime] = {}
    if date_from:
        created_filter["$gte"] = date_from
    if date_to:
        created_filter["$lte"] = date_to
    if created_filter:
        query["created_at_utc"] = created_filter

    projection = {
        "_id": 0,
        "created_at_utc": 1,
        "run_id": 1,
        "chat_hash": 1,
        "user_hash": 1,
        "message_id": 1,
        "msg_sha256": 1,
        "pred": 1,
        "score_1": 1,
        "latency_ms": 1,
        "ok": 1,
        "error": 1,
    }

    try:
        client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=1500)
        collection = client[settings.mongo_db][settings.mongo_collection]
        total = collection.count_documents(query)

        cursor = collection.find(query, projection).sort("created_at_utc", -1).skip(offset).limit(limit)

        items: list[dict[str, Any]] = []
        for doc in cursor:
            items.append(
                {
                    **doc,
                    "created_at_utc": _serialize_datetime(doc.get("created_at_utc")),
                }
            )

        client.close()
        return {
            "source": "mongo",
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
            "warning": None,
        }
    except Exception as exc:  # pragma: no cover - defensive for infra envs
        return {
            "source": "mongo_unavailable",
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": [],
            "warning": str(exc),
        }


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))
    if lower_index == upper_index:
        return float(ordered[lower_index])
    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    weight = position - lower_index
    return float(lower_value + (upper_value - lower_value) * weight)


def fetch_message_stats(
    settings: Settings,
    *,
    run_id: str | None,
    date_from: datetime | None,
    date_to: datetime | None,
    limit: int,
) -> dict[str, Any]:
    query: dict[str, Any] = {}
    if run_id:
        query["run_id"] = run_id

    created_filter: dict[str, datetime] = {}
    if date_from:
        created_filter["$gte"] = date_from
    if date_to:
        created_filter["$lte"] = date_to
    if created_filter:
        query["created_at_utc"] = created_filter

    projection = {
        "_id": 0,
        "pred": 1,
        "score_1": 1,
        "latency_ms": 1,
        "ok": 1,
    }

    try:
        client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=1500)
        collection = client[settings.mongo_db][settings.mongo_collection]
        cursor = collection.find(query, projection).sort("created_at_utc", -1).limit(limit)
        rows = list(cursor)
        client.close()

        total = len(rows)
        benign_count = sum(1 for row in rows if row.get("pred") == 0)
        threat_count = sum(1 for row in rows if row.get("pred") == 1)
        error_count = sum(1 for row in rows if row.get("ok") is False)

        latencies = [float(row["latency_ms"]) for row in rows if isinstance(row.get("latency_ms"), (int, float))]
        scores = [float(row["score_1"]) for row in rows if isinstance(row.get("score_1"), (int, float))]

        latency_avg = float(sum(latencies) / len(latencies)) if latencies else None
        score_avg = float(sum(scores) / len(scores)) if scores else None

        return {
            "source": "mongo",
            "total": total,
            "benign_count": benign_count,
            "threat_count": threat_count,
            "error_count": error_count,
            "error_rate": float(error_count / total) if total else 0.0,
            "latency_avg_ms": latency_avg,
            "latency_p95_ms": _percentile(latencies, 0.95),
            "score_avg": score_avg,
            "score_p50": _percentile(scores, 0.50),
            "score_p95": _percentile(scores, 0.95),
            "warning": None,
        }
    except Exception as exc:  # pragma: no cover - defensive for infra envs
        return {
            "source": "mongo_unavailable",
            "total": 0,
            "benign_count": 0,
            "threat_count": 0,
            "error_count": 0,
            "error_rate": 0.0,
            "latency_avg_ms": None,
            "latency_p95_ms": None,
            "score_avg": None,
            "score_p50": None,
            "score_p95": None,
            "warning": str(exc),
        }


def _default_training_metadata() -> dict[str, Any]:
    return {
        "script": "AITrainer_distilbert_2.py",
        "base_model": "distilbert-base-uncased",
        "freeze_policy": "all layers frozen except transformer.layer.5",
        "classifier_head": {
            "dropout_1": 0.3,
            "dense_units": 256,
            "activation": "ReLU",
            "dropout_2": 0.2,
            "output_units": 2,
        },
        "dataset": "balanced_dataset_generated.csv",
        "split": {"train": 0.9, "validation": 0.1, "random_state": 42},
        "hyperparameters": {
            "epochs": 4,
            "batch_size": 768,
            "learning_rate": 2e-5,
            "max_length": 64,
            "weight_decay": 0.01,
            "optimizer": "AdamW",
            "scheduler": "linear",
            "warmup_ratio": 0.1,
        },
        "task": "binary_classification",
        "labels": {"0": "Seguro", "1": "Sospechoso"},
        "privacy": {
            "pseudonymized_identifiers": ["user_hash", "chat_hash"],
            "optional_fields_disabled_by_default": ["msg_original", "msg_limpio", "tokens"],
            "retention_days_default": 30,
        },
    }


def load_training_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _default_training_metadata()

    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    merged = _default_training_metadata()
    merged.update(payload)
    return merged
