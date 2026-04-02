# TFG de Ingenieria de Computadores - Deteccion de Phishing en Telegram

Este directorio contiene la version del TFG de Ingenieria de Computadores orientada a sistemas, integracion y observabilidad. El foco academico ya no esta solo en clasificar mensajes, sino en defender un pipeline desacoplado y medible:

- producer de Telegram;
- cola RabbitMQ para desacoplar ingesta e inferencia;
- worker de inferencia y persistencia en MongoDB;
- API FastAPI para consulta y trazabilidad;
- frontend React para inspeccion funcional;
- Prometheus + Grafana para observabilidad operativa;
- benchmark controlado para estudiar latencia, throughput y uso de recursos.

## Enfoque academico

El peso del TFG esta en:

- arquitectura de pipeline extremo a extremo;
- integracion entre componentes desacoplados;
- observabilidad real con metricas exportables;
- benchmark controlado y defendible;
- decisiones de despliegue y trade-offs de sistemas.

La clasificacion forma parte del sistema, pero no es el centro academico del trabajo. Lo relevante es como se conectan cola, worker, persistencia, API y monitorizacion para construir un flujo operable y justificable.

## Componentes principales

- `producer.py`: escucha Telegram y publica eventos en RabbitMQ.
- `worker.py`: consume la cola, ejecuta inferencia y persiste evidencia tecnica en MongoDB.
- `main.py`: entry point compatible con modos `legacy`, `producer` y `worker`.
- `pipeline.py`: logica comun de preprocesado, inferencia, trazabilidad y latencias por etapa.
- `messaging.py`: adaptador RabbitMQ.
- `observability.py`: metricas Prometheus y snapshots de recursos con `psutil`.
- `api/`: API FastAPI con endpoints de runs, mensajes, stats, benchmarks y `/metrics`.
- `dashboard-react/`: dashboard operativo servido en Compose como `frontend`.
- `prometheus/`: configuracion de scraping para API y worker.
- `grafana/`: dashboards Prometheus para rendimiento, cola y benchmark.
- `scripts/simulate_cases.py`: simulacion E2E de casos operativos.
- `scripts/benchmark_pipeline.py`: benchmark controlado para 1, 5, 10 y 20 mensajes/segundo.
- `scripts/run_phase5_checks.py`: runner de validacion integrada.
- `docs/`: memoria, contrato API y metadatos tecnicos.

## Arquitectura del despliegue

Flujo base:

`rabbitmq + mongo + worker + api + frontend`

Flujo avanzado:

`producer -> rabbitmq -> worker -> mongo -> api -> frontend`

Observabilidad:

`worker/api -> Prometheus -> Grafana`

## Instalacion local y validacion

Desde esta carpeta, instala dependencias y ejecuta pruebas:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m scripts.benchmark_pipeline --dry-run
```

El comando canonico de validacion automatizada sigue siendo `python -m pytest -q`.

## Ejecucion funcional con Docker Compose

### 1. Preparar variables

```powershell
Copy-Item .env.example .env
```

Revisa al menos:

- `API_KEY`
- `MONGO_URI`
- `MONGO_DB`
- `MONGO_COLLECTION`
- `RABBITMQ_URL`
- `RABBITMQ_QUEUE`
- `REPORTS_DIR`
- `TRAINING_METADATA_PATH`

### 2. Levantar el stack base

```powershell
docker compose up --build
```

Este comando levanta:

- MongoDB;
- RabbitMQ;
- worker;
- API;
- dashboard React.

### 3. Observabilidad completa

```powershell
docker compose --profile observability up --build
```

Anade:

- Prometheus en `http://localhost:9090`
- Grafana en `http://localhost:3000`

### 4. Productor real de Telegram

```powershell
docker compose --profile advanced up --build
```

Antes de usarlo, completa credenciales reales:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_PHONE`

## Puertos y accesos

| Servicio | Puerto | Acceso |
| --- | --- | --- |
| frontend React | `5173` | `http://localhost:5173` |
| API FastAPI | `8000` | `http://localhost:8000` |
| RabbitMQ Management | `15672` | `http://localhost:15672` |
| Prometheus | `9090` | `http://localhost:9090` |
| Grafana | `3000` | `http://localhost:3000` |
| MongoDB | interno | solo red de Compose |
| worker metrics | interno `9108` | scrapeado por Prometheus |

## Endpoints principales

- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/thresholds`
- `GET /api/v1/runs/{run_id}/confusion-matrix`
- `GET /api/v1/messages`
- `GET /api/v1/messages/stats`
- `GET /api/v1/benchmarks`
- `GET /api/v1/benchmarks/{benchmark_id}`
- `GET /api/v1/training/metadata`
- `GET /metrics`

## Latencias y observabilidad

Cada mensaje puede exponer:

- `preprocess_latency_ms`
- `inference_latency_ms`
- `db_write_latency_ms`
- `queue_wait_latency_ms`
- `end_to_end_latency_ms`
- `cpu_percent`
- `rss_bytes`
- `vms_bytes`
- `queue_depth`

Se mantiene `latency_ms` por compatibilidad, equivalente a la latencia de inferencia.

## Benchmark controlado

Benchmark rapido:

```powershell
python -m scripts.benchmark_pipeline --duration-seconds 5 --rates 1 5 10 20
```

El benchmark guarda artefactos en `reports/benchmarks/<benchmark_id>/` con:

- throughput real;
- latencia media y p95;
- CPU media;
- RAM media;
- tasa de errores.

## Artefactos

- evaluacion offline: `reports/runs/<run_id>/`
- validacion integrada: `reports/validations/<validation_id>/`
- benchmark controlado: `reports/benchmarks/<benchmark_id>/`

La raiz de `reports/` mantiene copias rapidas del ultimo estado para consumo operativo.
