# API Contract

Base URL local: `http://localhost:8000`

## Autenticacion

Todos los endpoints bajo `/api/v1/*` requieren:

```http
X-API-Key: <API_KEY>
```

El endpoint `/metrics` queda sin autenticacion porque esta pensado para `Prometheus`.

## Endpoints

### `GET /api/v1/health`

Comprueba disponibilidad de MongoDB y de los artefactos en `reports/`.

```json
{
  "status": "ok|degraded",
  "timestamp_utc": "2026-04-02T15:40:00.000000+00:00",
  "mongo_ok": true,
  "reports_ok": true,
  "details": {}
}
```

### `GET /api/v1/runs`

Devuelve el historico de evaluaciones offline versionadas por `run_id`.

```json
{
  "runs": [
    {
      "run_id": "63c1d8a6-613a-4971-b3bf-dc0fe2907001",
      "timestamp": "2026-03-18 19:47:52",
      "hf_model": "alvaroosuna/distilbert_fast_fixed_labels",
      "model_source": "state_dict:... base:distilbert-base-uncased",
      "threshold": 0.05,
      "num_samples": 100,
      "label_distribution": {
        "0": 50,
        "1": 50
      },
      "metrics": {
        "accuracy": 0.63,
        "precision_pos": 0.5823,
        "recall_pos": 0.92,
        "f1_pos": 0.7132,
        "roc_auc": 0.8684,
        "average_precision": 0.8951
      }
    }
  ]
}
```

### `GET /api/v1/runs/{run_id}/summary`

Devuelve el resumen normalizado de un `run_id`.

### `GET /api/v1/runs/{run_id}/thresholds`

Lee `threshold_analysis.csv` del directorio canonico del `run_id`.

```json
{
  "run_id": "63c1d8a6-613a-4971-b3bf-dc0fe2907001",
  "points": [
    {
      "threshold": 0.05,
      "precision_pos": 0.5823,
      "recall_pos": 0.92,
      "f1_pos": 0.7132,
      "accuracy": 0.63
    }
  ]
}
```

### `GET /api/v1/runs/{run_id}/confusion-matrix`

Lee `confusion_matrix.csv` del directorio canonico del `run_id`.

```json
{
  "run_id": "63c1d8a6-613a-4971-b3bf-dc0fe2907001",
  "labels": [0, 1],
  "matrix": [[17, 33], [4, 46]],
  "normalized": [[0.34, 0.66], [0.08, 0.92]]
}
```

### `GET /api/v1/messages`

Consulta trazas persistidas en MongoDB.

Filtros disponibles:

- `run_id`
- `pred`
- `score_min`
- `date_from`
- `date_to`
- `limit`
- `offset`

Respuesta:

```json
{
  "source": "mongo|mongo_unavailable",
  "total": 120,
  "limit": 100,
  "offset": 0,
  "items": [
    {
      "created_at_utc": "2026-04-02T15:34:20.000000+00:00",
      "persisted_at_utc": "2026-04-02T15:34:20.051000+00:00",
      "source_received_at_utc": "2026-04-02T15:34:19.998000+00:00",
      "queued_at_utc": "2026-04-02T15:34:20.000000+00:00",
      "run_id": "bench-20260402T153415Z-b54ed0d2",
      "source": "benchmark|telegram",
      "channel": "benchmark_10msg_s",
      "chat_hash": "sha256",
      "user_hash": "sha256",
      "message_id": 42,
      "msg_sha256": "hex",
      "pred": 1,
      "score_1": 0.93,
      "latency_ms": 24.7,
      "preprocess_latency_ms": 1.1,
      "inference_latency_ms": 24.7,
      "db_write_latency_ms": 0.8,
      "queue_wait_latency_ms": 2.0,
      "end_to_end_latency_ms": 28.6,
      "queue_depth": 3,
      "cpu_percent": 712.5,
      "rss_bytes": 946712576,
      "vms_bytes": 2043148288,
      "gpu_memory_bytes": null,
      "ok": true,
      "error": null
    }
  ],
  "warning": null
}
```

Notas:

- `latency_ms` se mantiene por compatibilidad y equivale a la latencia principal de inferencia.
- `cpu_percent` es la medicion del proceso y puede superar `100` en maquinas multinucleo.
- Si MongoDB no esta disponible, la API responde con `source = "mongo_unavailable"` y `warning`.

### `GET /api/v1/messages/stats`

Agrega trazas recientes y expone estadisticas operativas.

Filtros disponibles:

- `run_id`
- `date_from`
- `date_to`
- `limit`

```json
{
  "source": "mongo",
  "total": 100,
  "benign_count": 31,
  "threat_count": 69,
  "error_count": 0,
  "error_rate": 0.0,
  "latency_avg_ms": 52.396,
  "latency_p95_ms": 66.06005,
  "preprocess_latency_avg_ms": 0.842,
  "preprocess_latency_p95_ms": 1.517,
  "inference_latency_avg_ms": 51.112,
  "inference_latency_p95_ms": 64.801,
  "db_write_latency_avg_ms": 0.0,
  "db_write_latency_p95_ms": 0.0,
  "end_to_end_latency_avg_ms": 52.396,
  "end_to_end_latency_p95_ms": 66.06005,
  "queue_wait_latency_avg_ms": 0.0,
  "queue_wait_latency_p95_ms": 0.0,
  "queue_depth_avg": 0.0,
  "queue_depth_p95": 0.0,
  "score_avg": 0.814,
  "score_p50": 0.932,
  "score_p95": 0.997,
  "cpu_avg_percent": 773.571,
  "rss_avg_bytes": 946963251.2,
  "vms_avg_bytes": 2043159019.52,
  "gpu_memory_avg_bytes": null,
  "throughput_messages_per_second": 19.081,
  "warning": null
}
```

### `GET /api/v1/benchmarks`

Lista benchmarks controlados disponibles en `reports/benchmarks/`.

```json
{
  "benchmarks": [
    {
      "benchmark_id": "bench-20260402T153415Z-b54ed0d2",
      "created_at_utc": "2026-04-02T15:34:39.321414+00:00",
      "duration_seconds_per_scenario": 5,
      "write_mongo": false,
      "artifacts_dir": "benchmarks/bench-20260402T153415Z-b54ed0d2",
      "scenarios": [
        {
          "scenario": "10msg_s",
          "target_rate_mps": 10,
          "planned_messages": 50,
          "processed_messages": 50,
          "throughput_mps": 10.092,
          "latency_avg_ms": 52.287,
          "latency_p95_ms": 63.98635,
          "cpu_avg_percent": 737.648,
          "ram_avg_bytes": 946964889.6,
          "vms_avg_bytes": 2043301888.0,
          "error_rate": 0.0
        }
      ],
      "artifacts": {
        "samples_csv": "benchmarks/bench-20260402T153415Z-b54ed0d2/benchmark_samples.csv",
        "summary_json": "benchmarks/bench-20260402T153415Z-b54ed0d2/benchmark_summary.json"
      }
    }
  ]
}
```

### `GET /api/v1/benchmarks/{benchmark_id}`

Devuelve el detalle completo de un benchmark concreto.

### `GET /api/v1/training/metadata`

Expone metadatos del modelo integrado y de la politica de privacidad por defecto.

### `GET /metrics`

Endpoint Prometheus para scraping sin autenticacion.

Series relevantes:

- `tfg_api_requests_total`
- `tfg_api_request_latency_ms`
- `tfg_messages_processed_total`
- `tfg_messages_errors_total`
- `tfg_inference_latency_ms`
- `tfg_end_to_end_latency_ms`
- `tfg_queue_depth`
- `tfg_process_cpu_percent`
- `tfg_process_rss_bytes`

## Artefactos asociados

- Evaluacion offline: `reports/runs/<run_id>/`
- Benchmark: `reports/benchmarks/<benchmark_id>/`
- Copia rapida del ultimo benchmark: `reports/benchmark_summary.json`
- Metadatos de entrenamiento: `docs/training_metadata.json`
