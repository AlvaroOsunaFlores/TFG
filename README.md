# MVP TFG - Telegram + IA + Mongo + API + Dashboard

Este repositorio cubre Fase 4 y Fase 5 del TFG:
- ingesta de mensajes de Telegram,
- clasificacion binaria de ciberseguridad (0 benigno / 1 amenaza),
- trazabilidad en MongoDB,
- evaluacion offline con metricas reproducibles,
- API FastAPI para consumo de resultados,
- dashboard React + Chart.js,
- panelizacion Grafana MVP,
- validacion E2E con casos simulados.

## Componentes principales
- `main.py`: bot en tiempo real (Telethon + inferencia + Mongo).
- `evaluate.py`: evaluacion offline y generacion de artefactos en `reports/`.
- `api/`: FastAPI con endpoints `/api/v1/...`.
- `dashboard-react/`: frontend para visualizacion.
- `scripts/simulate_cases.py`: casos simulados para Fase 5.
- `scripts/run_phase5_checks.py`: runner de validacion de integracion.
- `grafana/`: provision de datasource y dashboard MVP.
- `docs/`: memoria y documentacion.

## Variables de entorno
Base (`.env.example`):
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
- `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`
- `HF_MODEL`, `THRESHOLD` (por defecto `0.05`, orientado a recall alto)
- `HF_BASE_MODEL`, `HF_STATE_DICT_FILE`
- `REPORTS_DIR`, `TRAINING_METADATA_PATH`

## Flujo rapido
1. Copia variables:
```bash
cp .env.example .env
```

2. Construye y levanta servicios:
```bash
docker compose build
docker compose up
```

Servicios disponibles:
- Bot: `telegram_bot`
- API: `http://localhost:8000`
- Grafana: `http://localhost:3000` (`admin` / `admin`)

3. Ejecuta evaluacion offline:
```bash
docker compose run --rm bot python evaluate.py
```

4. Ejecuta simulacion E2E (Fase 5):
```bash
docker compose run --rm bot python scripts/simulate_cases.py --write-mongo
```

5. Ejecuta validacion de fase completa:
```bash
docker compose run --rm bot python scripts/run_phase5_checks.py --write-mongo
```

## API FastAPI
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
```bash
npm install
npm run dev
```
Configura `dashboard-react/.env` con:
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Artefactos en `reports/`
- `metrics.json`
- `predictions.csv`
- `confusion_matrix.csv`
- `threshold_analysis.csv`
- `simulated_cases_results.csv`
- `e2e_evidence.json`
- `phase5_validation.json`

## Memoria
- Fuente principal: `docs/MEMORIA_TFG_ETSII_APA7.md`
- Entregable DOCX: `docs/MEMORIA_TFG_ETSII_APA7.docx`
- Regeneracion reproducible:
```bash
python scripts/build_memoria_docx.py
```

## Notas de seguridad
- No subas `.env` ni `session/*.session`.
- No incluyas credenciales reales en anexos o capturas.
