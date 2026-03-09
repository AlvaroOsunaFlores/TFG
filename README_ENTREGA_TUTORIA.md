# README Entrega Tutoria

## Contenido entregado
Esta entrega incluye:
- código del bot de Telegram + inferencia (`main.py`);
- evaluación reproducible (`evaluate.py`) y reportes versionados en `reports/`;
- API FastAPI (`api/`) con control por `X-API-Key`;
- dashboard React (`dashboard-react/`) para visualización operativa;
- provisioning de Grafana (`grafana/`) sin acceso anónimo;
- scripts de validación E2E (`scripts/`);
- tests de API (`tests/`);
- documentación técnica y memoria en `docs/`.

## Endurecimiento aplicado
- MongoDB ya no queda expuesto por puerto público en Docker.
- Grafana requiere autenticación de administrador.
- La API no deja endpoints abiertos.
- CORS queda restringido a orígenes locales definidos en `.env`.
- La persistencia por defecto minimiza datos sensibles y pseudonimiza identificadores.

## Ejecución mínima recomendada

### 1) Variables de entorno
```powershell
Copy-Item .env.example .env
```
Completar al menos credenciales Telegram, `API_KEY`, `PII_SALT` y credenciales de Grafana.

### 2) Dependencias locales
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3) Evaluación offline
```powershell
python evaluate.py
```
Salidas esperadas:
- `reports/metrics.json`
- `reports/confusion_matrix.csv`
- `reports/predictions.csv`
- `reports/threshold_analysis.csv`
- `reports/runs/<run_id>/...` como fuente canónica

### 4) Validación Fase 5
```powershell
python -m scripts.run_phase5_checks --skip-evaluate --write-mongo
```
Salida principal:
- `reports/phase5_validation.json`
- `reports/validations/<validation_id>/phase5_validation.json`

## Arranque por servicios

### FastAPI
```powershell
uvicorn api.app:app --host 0.0.0.0 --port 8000
```
Usar siempre:
```text
X-API-Key: <API_KEY>
```

### Dashboard React
```powershell
cd dashboard-react
Copy-Item .env.example .env
npm install
npm run dev
```
Variables mínimas:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=<API_KEY>
```

### Grafana
Con `docker compose up` se provisiona automáticamente desde:
- `grafana/provisioning/datasources/datasource.yml`
- `grafana/provisioning/dashboards/dashboard.yml`
- `grafana/dashboards/tfg_mvp_dashboard.json`

## Notas operativas
- Si hay limitaciones de memoria GPU, forzar CPU:
```powershell
$env:CUDA_VISIBLE_DEVICES=""
python -m scripts.run_phase5_checks --skip-evaluate --write-mongo
```
- No incluir `.env`, sesiones de Telegram ni secretos en entregas externas.
- `msg_original`, `msg_limpio` y `tokens` permanecen desactivados salvo necesidad real y justificada.
