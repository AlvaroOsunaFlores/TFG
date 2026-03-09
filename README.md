# MVP TFG - Telegram + IA + Mongo + API + Dashboard

Este repositorio cubre la parte operativa del TFG:
- ingesta de mensajes de Telegram,
- clasificación binaria de ciberseguridad (`0=benigno`, `1=amenaza`),
- trazabilidad mínima y pseudonimizada en MongoDB,
- evaluación offline con métricas reproducibles,
- API FastAPI protegida por clave,
- dashboard React,
- panelización Grafana MVP,
- validación E2E con casos simulados.

## Cambios clave de esta iteración
- Mongo deja de exponerse públicamente en `docker-compose`.
- Grafana deja de aceptar acceso anónimo.
- La API exige `X-API-Key` en todos los endpoints.
- CORS queda restringido a orígenes locales explícitos.
- La persistencia por defecto minimiza datos: `user_hash`, `chat_hash`, `message_id`, `msg_sha256`, `pred`, `score_1`, `latency_ms`, `run_id`.
- Los artefactos se versionan por ejecución en `reports/runs/<run_id>/`.

## Componentes principales
- `main.py`: bot en tiempo real (Telethon + inferencia + Mongo).
- `evaluate.py`: evaluación offline y generación de artefactos versionados.
- `api/`: FastAPI con endpoints `/api/v1/...`.
- `dashboard-react/`: frontend de visualización.
- `scripts/simulate_cases.py`: casos simulados para Fase 5.
- `scripts/run_phase5_checks.py`: runner de validación.
- `grafana/`: provisioning del datasource y dashboard.
- `docs/`: memoria, contrato API y documentación de apoyo.

## Variables de entorno
Base (`.env.example`):
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
- `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`
- `HF_MODEL`, `THRESHOLD`
- `API_KEY`, `API_CORS_ORIGINS`
- `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`
- `PII_SALT`, `STORE_MSG_ORIGINAL`, `STORE_MSG_NORMALIZED`, `STORE_NLP_FEATURES`, `RETENTION_DAYS`
- `HF_BASE_MODEL`, `HF_STATE_DICT_FILE`
- `REPORTS_DIR`, `TRAINING_METADATA_PATH`

## Flujo rápido
1. Copia variables:
```powershell
Copy-Item .env.example .env
```

2. Levanta servicios:
```powershell
docker compose build
docker compose up
```

Servicios publicados:
- API: `http://localhost:8000`
- Grafana: `http://localhost:3000`

3. Ejecuta evaluación offline:
```powershell
python evaluate.py
```

4. Ejecuta simulación E2E:
```powershell
python -m scripts.simulate_cases --write-mongo
```

5. Ejecuta validación Fase 5:
```powershell
python -m scripts.run_phase5_checks --write-mongo
```

## Artefactos en `reports/`
- Último resultado compatible en raíz:
  - `metrics.json`
  - `predictions.csv`
  - `confusion_matrix.csv`
  - `threshold_analysis.csv`
  - `simulated_cases_results.csv`
  - `e2e_evidence.json`
  - `phase5_validation.json`
- Resultado canónico por ejecución:
  - `reports/runs/<run_id>/...`
  - `reports/validations/<validation_id>/phase5_validation.json`

## API FastAPI
Todos los endpoints requieren cabecera:
```text
X-API-Key: <API_KEY>
```

Contratos implementados:
- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/thresholds`
- `GET /api/v1/runs/{run_id}/confusion-matrix`
- `GET /api/v1/messages`
- `GET /api/v1/messages/stats`
- `GET /api/v1/training/metadata`

## Dashboard React
Dentro de `dashboard-react/`:
```powershell
npm install
npm run dev
```

Configura `dashboard-react/.env` con:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=<API_KEY>
```

## Memoria y documentos
- Fuente canónica: `docs/MEMORIA_TFG_ETSII_APA7.md`
- Contrato API: `docs/API_CONTRACT.md`
- Resumen para lectura rápida: `docs/GUIA_SISTEMA_PARA_DUMMIES.md`

## Notas de seguridad
- No subas `.env` ni `session/*.session`.
- No dejes `API_KEY`, `PII_SALT` ni credenciales de Grafana en valores de ejemplo.
- `msg_original`, `msg_limpio` y `tokens` están desactivados por defecto.
- La retención mínima por defecto es de 30 días mediante TTL en Mongo.
