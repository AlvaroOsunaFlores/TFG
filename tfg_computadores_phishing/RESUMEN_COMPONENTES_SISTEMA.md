# Resumen de Componentes del Sistema

## Objetivo del sistema
Pipeline end-to-end para detectar mensajes potencialmente maliciosos en Telegram, dejar evidencia técnica suficiente para auditar la decisión y visualizar resultados sin exponer más datos de los necesarios.

## 1) Bot de ingesta e inferencia (`main.py`)
- escucha mensajes con Telethon;
- preprocesa texto y detecta idioma;
- ejecuta clasificación binaria (`0=benigno`, `1=amenaza`);
- guarda en MongoDB una traza mínima:
  - `run_id`,
  - `message_id`,
  - `user_hash`,
  - `chat_hash`,
  - `msg_sha256`,
  - `pred`,
  - `score_1`,
  - `latency_ms`,
  - `created_at_utc`,
  - `hf_model`, `model_source`, `device`.

## 2) Evaluación offline (`evaluate.py`)
- usa `data/test.csv`;
- genera artefactos por ejecución en `reports/runs/<run_id>/`;
- deja copia del último run en `reports/` para uso rápido;
- incluye metadatos reproducibles: hash del dataset, versiones y origen del modelo.

## 3) API de explotación (`api/`)
- servicio FastAPI para exponer métricas, runs y trazabilidad;
- todos los endpoints requieren `X-API-Key`;
- los endpoints por `run_id` leen artefactos del directorio correcto del run;
- la respuesta de mensajes evita IDs crudos y usa identificadores pseudonimizados.

## 4) Dashboard web (`dashboard-react/`)
- frontend React + Chart.js;
- consume la API con `VITE_API_BASE_URL` y `VITE_API_KEY`;
- muestra KPIs, curva por umbral, matriz de confusión y tabla de mensajes.

## 5) Observabilidad en Grafana (`grafana/`)
- provisioning automático de datasource y dashboard;
- autenticación activa, sin acceso anónimo;
- consume la API añadiendo `X-API-Key`.

## 6) Validación de integración (`scripts/`)
- `scripts/simulate_cases.py`: ejecuta casos simulados;
- `scripts/run_phase5_checks.py`: deja evidencia consolidada;
- genera:
  - `reports/simulated_cases_results.csv`,
  - `reports/e2e_evidence.json`,
  - `reports/phase5_validation.json`,
  - `reports/validations/<validation_id>/phase5_validation.json`.

## Flujo integrado
1. Telegram entra en `main.py`.
2. El modelo devuelve `pred` y `score_1`.
3. MongoDB guarda solo la evidencia mínima y pseudonimizada.
4. `evaluate.py` genera métricas reproducibles por `run_id`.
5. FastAPI publica esos resultados.
6. Dashboard React y Grafana consumen la API.

## Decisiones de trazabilidad
- `run_id` identifica una ejecución completa.
- `msg_sha256` permite demostrar integridad sin guardar siempre el texto original.
- `user_hash` y `chat_hash` mantienen trazabilidad sin exponer PII directa.
- `THRESHOLD=0.05` se mantiene como decisión operativa orientada a recall alto.
