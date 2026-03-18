# TFG de Ingenieria de Computadores - Deteccion de Phishing en Telegram

Este proyecto corresponde al TFG orientado a sistemas e integracion. El foco principal no esta solo en la clasificacion, sino en el pipeline operativo completo:

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
- `dashboard-react/`: dashboard operativo.
- `grafana/`: monitorizacion complementaria.
- `scripts/simulate_cases.py`: simulacion E2E de casos operativos.
- `scripts/run_phase5_checks.py`: runner de validacion integrada.
- `docs/`: memoria, contrato API y documentacion de apoyo.

## Ejecucion basica

Desde esta carpeta:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Entorno virtual compartido

Si reutilizas el entorno virtual existente en la raiz del repo:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe evaluate.py
```

Si prefieres un entorno virtual propio para este TFG, puedes crearlo dentro de esta carpeta sin afectar al resto del repositorio.

## Endpoints principales

Todos requieren:

```text
X-API-Key: <API_KEY>
```

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

- fuente canonica: `docs/MEMORIA_TFG_ETSII_APA7.md`
- DOCX generado: `docs/MEMORIA_TFG_ETSII_APA7.docx`
- resumen rapido: `docs/GUIA_SISTEMA_PARA_DUMMIES.md`
