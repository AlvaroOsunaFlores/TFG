from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app
from api.settings import Settings


def _build_reports(base_dir: Path) -> Path:
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics_payload = {
        "run_id": "run-test-001",
        "timestamp": "2026-02-12 22:23:28",
        "hf_model": "alvaroosuna/distilbert_fast_fixed_labels",
        "model_source": "state_dict:demo",
        "threshold": 0.05,
        "num_samples": 100,
        "label_distribution": {"0": 50, "1": 50},
        "metrics": {
            "accuracy": 0.82,
            "precision_pos": 0.58,
            "recall_pos": 0.92,
            "f1_pos": 0.71,
            "roc_auc": 0.86,
            "average_precision": 0.89,
        },
    }
    (reports_dir / "metrics.json").write_text(json.dumps(metrics_payload), encoding="utf-8")

    (reports_dir / "threshold_analysis.csv").write_text(
        "threshold,precision_pos,recall_pos,f1_pos,accuracy\n"
        "0.05,0.58,0.92,0.71,0.63\n"
        "0.5,0.82,0.82,0.82,0.82\n",
        encoding="utf-8",
    )

    (reports_dir / "confusion_matrix.csv").write_text(
        ",0,1\n"
        "0,31,19\n"
        "1,4,46\n",
        encoding="utf-8",
    )

    return reports_dir


def _build_metadata(base_dir: Path) -> Path:
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = docs_dir / "training_metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "script": "AITrainer_distilbert_2.py",
                "hyperparameters": {"epochs": 4, "batch_size": 768},
            }
        ),
        encoding="utf-8",
    )
    return metadata_path


def _client(base_dir: Path) -> TestClient:
    reports_dir = _build_reports(base_dir)
    metadata_path = _build_metadata(base_dir)

    settings = Settings(
        reports_dir=reports_dir,
        mongo_uri="mongodb://invalid-host:27017/",
        mongo_db="tfg",
        mongo_collection="messages",
        training_metadata_path=metadata_path,
        cors_origins=["*"],
    )

    app = create_app(settings)
    return TestClient(app)


def test_health_endpoint(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["reports_ok"] is True
    assert payload["mongo_ok"] is False
    assert payload["status"] == "degraded"


def test_runs_and_summary(tmp_path: Path) -> None:
    client = _client(tmp_path)

    runs_response = client.get("/api/v1/runs")
    assert runs_response.status_code == 200
    assert len(runs_response.json()["runs"]) == 1

    summary_response = client.get("/api/v1/runs/run-test-001/summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["metrics"]["recall_pos"] == 0.92


def test_thresholds_and_confusion(tmp_path: Path) -> None:
    client = _client(tmp_path)

    thresholds = client.get("/api/v1/runs/run-test-001/thresholds")
    assert thresholds.status_code == 200
    assert len(thresholds.json()["points"]) == 2

    confusion = client.get("/api/v1/runs/run-test-001/confusion-matrix")
    assert confusion.status_code == 200
    payload = confusion.json()
    assert payload["labels"] == [0, 1]
    assert payload["matrix"][0] == [31, 19]
    assert payload["normalized"][1][1] > 0.9


def test_training_metadata(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get("/api/v1/training/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["script"] == "AITrainer_distilbert_2.py"


def test_messages_endpoint_when_mongo_unavailable(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get("/api/v1/messages", params={"run_id": "run-test-001", "limit": 10})
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "mongo_unavailable"
    assert payload["items"] == []
