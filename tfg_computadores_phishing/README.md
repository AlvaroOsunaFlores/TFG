# TFG de Ingenieria de Computadores - Deteccion de Phishing en Telegram

Este directorio contiene la version final del TFG de Ingenieria de Computadores orientado a sistemas e integracion. El foco principal no esta solo en la clasificacion, sino en el pipeline operativo completo:

- ingesta de mensajes de Telegram;
- preprocesamiento e inferencia;
- persistencia trazable en MongoDB;
- evaluacion offline reproducible;
- exposicion de resultados por API;
- visualizacion y monitorizacion en React y Grafana;
- validacion extremo a extremo de la integracion.

## Enfoque academico

El proyecto se presenta como un sistema modular para la deteccion de phishing y mensajes sospechosos, poniendo el peso en:

- arquitectura del pipeline extremo a extremo;
- integracion entre componentes;
- ejecucion sobre infraestructura local o contenerizada;
- observabilidad y trazabilidad operativa;
- endurecimiento minimo de seguridad en la explotacion.

## Componentes principales

- `main.py`: escucha de Telegram, preprocesado, inferencia y persistencia.
- `evaluate.py`: evaluacion offline y generacion de metricas por `run_id`.
- `api/`: API FastAPI protegida por `X-API-Key`.
- `dashboard-react/`: dashboard operativo servido en Compose como `frontend`.
- `grafana/`: monitorizacion complementaria.
- `scripts/simulate_cases.py`: simulacion E2E de casos operativos.
- `scripts/run_phase5_checks.py`: runner de validacion integrada.
- `docs/`: memoria final, contrato API, metadatos y figuras incluidas en la documentacion.

## Alcance para la entrega funcional

- obligatorio: `mongo + api + frontend`
- opcional: `grafana`
- avanzado: `bot`

El servicio `bot` queda como escenario avanzado porque requiere credenciales reales de Telegram (`TELEGRAM_API_ID`, `TELEGRAM_API_HASH` y `TELEGRAM_PHONE`) para arrancar correctamente.

## Instalacion local y validacion

Desde esta carpeta, el flujo recomendado es crear o activar un entorno virtual y despues instalar dependencias antes de lanzar pruebas.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python evaluate.py
```

El comando canonico de validacion es `python -m pytest -q`.

Si `python -m pytest -q` falla con un error de dependencia como `pymongo`, el problema no esta en el proyecto sino en no haber ejecutado antes `python -m pip install -r requirements.txt`.

## Ejecucion funcional con Docker Compose

### 1. Preparar variables

```powershell
Copy-Item .env.example .env
```

Para la correccion funcional minima, revisa al menos estas variables en `.env`:

- `API_KEY`
- `MONGO_URI`
- `MONGO_DB`
- `MONGO_COLLECTION`
- `TRAINING_METADATA_PATH`
- `REPORTS_DIR`

### 2. Levantar el stack obligatorio

```powershell
docker compose up --build
```

Por defecto este comando levanta solo el flujo obligatorio de la entrega: MongoDB, API y dashboard React.

### 3. Acceder a los servicios

- frontend React: `http://localhost:5173`
- API FastAPI: `http://localhost:8000`

Todos los endpoints protegidos de la API requieren la cabecera:

```text
X-API-Key: <API_KEY>
```

## Servicios opcionales y avanzados

Para anadir Grafana a la ejecucion:

```powershell
docker compose --profile observability up --build
```

Para anadir el bot de Telegram al despliegue:

```powershell
docker compose --profile advanced up --build
```

Antes de usar el perfil `advanced`, completa en `.env` estas credenciales reales:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`

## Variables por escenario

- flujo obligatorio `mongo + api + frontend`: `API_KEY`, `MONGO_URI`, `MONGO_DB`, `MONGO_COLLECTION`, `TRAINING_METADATA_PATH`, `REPORTS_DIR`
- grafana opcional: `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`
- bot avanzado: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
- privacidad opcional: `PII_SALT`, `STORE_MSG_ORIGINAL`, `STORE_MSG_NORMALIZED`, `STORE_NLP_FEATURES`, `RETENTION_DAYS`

El servicio `frontend` recibe `VITE_API_BASE_URL=http://localhost:8000` y `VITE_API_KEY=${API_KEY}` desde Compose para consumir la API publicada en el host.

## Puertos y accesos

| Servicio | Puerto | Acceso |
| --- | --- | --- |
| frontend React | `5173` | publico en `http://localhost:5173` |
| API FastAPI | `8000` | publico en `http://localhost:8000` |
| Grafana | `3000` | publico en `http://localhost:3000` cuando se activa el perfil `observability` |
| MongoDB | `27017` | solo interno en la red de Compose, sin publicacion al host |
| bot | sin puerto | proceso interno, sin endpoint HTTP publico |

## Endpoints principales

- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/thresholds`
- `GET /api/v1/runs/{run_id}/confusion-matrix`
- `GET /api/v1/messages`
- `GET /api/v1/messages/stats`
- `GET /api/v1/training/metadata`

## Artefactos

Los artefactos tecnicos viven en `reports/runs/<run_id>/`, mientras que la raiz de `reports/` mantiene una copia rapida del ultimo estado para compatibilidad operativa.

## Memoria

- memoria editable: `docs/MEMORIA_TFG_ETSII_APA7.docx`
- memoria en PDF: `docs/MEMORIA_TFG_ETSII_APA7.pdf`
- fuente de trabajo: `docs/MEMORIA_TFG_ETSII_APA7.md`
