# API Contract (FastAPI)

Base URL: `http://localhost:8000`

## Autenticación
Todos los endpoints requieren:
```http
X-API-Key: <API_KEY>
```

## Endpoints

### `GET /api/v1/health`
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
Lee `threshold_analysis.csv` del directorio canónico del `run_id`.

### `GET /api/v1/runs/{run_id}/confusion-matrix`
Lee `confusion_matrix.csv` del directorio canónico del `run_id`.

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
      "chat_hash": "sha256",
      "user_hash": "sha256",
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

### `GET /api/v1/messages/stats`
Filtros:
- `run_id` (opcional)
- `date_from`, `date_to` (ISO datetime)
- `limit` (1..5000)

### `GET /api/v1/training/metadata`
Devuelve metadatos del entrenamiento documentado y la política de privacidad por defecto.
