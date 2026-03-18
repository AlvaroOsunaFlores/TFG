# FastAPI (Fase 4/5)

Servicio de explotacion de resultados y trazabilidad del sistema.

## Arranque local
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints principales
- `/api/v1/health`
- `/api/v1/runs`
- `/api/v1/runs/{run_id}/summary`
- `/api/v1/runs/{run_id}/thresholds`
- `/api/v1/runs/{run_id}/confusion-matrix`
- `/api/v1/messages`
- `/api/v1/training/metadata`

## Configuracion
Variables relevantes:
- `REPORTS_DIR`
- `MONGO_URI`
- `MONGO_DB`
- `MONGO_COLLECTION`
- `TRAINING_METADATA_PATH`
