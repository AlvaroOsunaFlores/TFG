# API Contract (FastAPI)

Base URL: `http://localhost:8000`

## Endpoints

### `GET /api/v1/health`
Respuesta:
```json
{
  "status": "ok|degraded",
  "timestamp_utc": "2026-03-01T18:20:00.000000",
  "mongo_ok": true,
  "reports_ok": true,
  "details": {}
}
```

### `GET /api/v1/runs`
Respuesta:
```json
{
  "runs": [
    {
      "run_id": "uuid",
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "hf_model": "model-id",
      "model_source": "state_dict:...",
      "threshold": 0.05,
      "num_samples": 100,
      "label_distribution": {"0": 50, "1": 50},
      "metrics": {
        "accuracy": 0.82,
        "precision_pos": 0.58,
        "recall_pos": 0.92,
        "f1_pos": 0.71,
        "roc_auc": 0.86,
        "average_precision": 0.89
      }
    }
  ]
}
```

### `GET /api/v1/runs/{run_id}/summary`
Respuesta: `RunSummary`.

### `GET /api/v1/runs/{run_id}/thresholds`
Respuesta:
```json
{
  "run_id": "uuid",
  "points": [
    {
      "threshold": 0.05,
      "precision_pos": 0.58,
      "recall_pos": 0.92,
      "f1_pos": 0.71,
      "accuracy": 0.63
    }
  ]
}
```

### `GET /api/v1/runs/{run_id}/confusion-matrix`
Respuesta:
```json
{
  "run_id": "uuid",
  "labels": [0, 1],
  "matrix": [[31, 19], [4, 46]],
  "normalized": [[0.62, 0.38], [0.08, 0.92]]
}
```

### `GET /api/v1/messages`
Filtros:
- `run_id` (opcional)
- `pred` (0|1)
- `score_min` (0..1)
- `date_from`, `date_to` (ISO datetime)
- `limit`, `offset`

Respuesta:
```json
{
  "source": "mongo|mongo_unavailable",
  "total": 120,
  "limit": 100,
  "offset": 0,
  "items": [
    {
      "created_at_utc": "2026-03-01T18:20:00+00:00",
      "run_id": "uuid",
      "chat_id": 12345,
      "message_id": 999,
      "msg_sha256": "hex",
      "pred": 1,
      "score_1": 0.93,
      "latency_ms": 25.1,
      "ok": true,
      "error": null
    }
  ],
  "warning": null
}
```

### `GET /api/v1/training/metadata`
Devuelve metadatos del entrenamiento documentado (`docs/training_metadata.json`).
