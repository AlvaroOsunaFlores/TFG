# Informe de Métricas y Trazabilidad

## 1. Qué se mide
- evaluación offline sobre `data/test.csv`;
- validación de integración con casos simulados;
- coherencia entre artefactos por `run_id`, API y dashboard.

## 2. Por qué `THRESHOLD=0.05`
- el sistema está orientado a detección preventiva;
- en este contexto es peor dejar pasar una amenaza real que revisar una falsa alarma;
- por eso se prioriza recall alto aunque suban los falsos positivos;
- el equilibrio alternativo queda documentado en `threshold_analysis.csv`.

## 3. Qué artefactos se generan
- `reports/runs/<run_id>/metrics.json`
- `reports/runs/<run_id>/predictions.csv`
- `reports/runs/<run_id>/threshold_analysis.csv`
- `reports/runs/<run_id>/confusion_matrix.csv`
- `reports/simulated_cases_results.csv`
- `reports/e2e_evidence.json`
- `reports/phase5_validation.json`

La raíz de `reports/` mantiene una copia del último resultado por compatibilidad, pero la fuente canónica es la carpeta del run.

## 4. Qué se guarda en Mongo
Por defecto:
- `run_id`
- `created_at_utc`
- `user_hash`
- `chat_hash`
- `message_id`
- `msg_sha256`
- `idioma`
- `pred`
- `score_1`
- `latency_ms`
- `ok`
- `error`
- `threshold`
- `hf_model`
- `model_source`
- `device`

Desactivado por defecto:
- `msg_original`
- `msg_limpio`
- `tokens`

## 5. Por qué esta trazabilidad es suficiente
- `run_id` une cada mensaje con la evaluación y con el dashboard;
- `msg_sha256` demuestra integridad del contenido sin guardar siempre el texto;
- `message_id` permite correlación técnica con el origen;
- `user_hash` y `chat_hash` permiten seguir patrones sin exponer identificadores reales;
- `threshold`, `pred` y `score_1` explican la decisión del modelo;
- `latency_ms`, `ok` y `error` explican cómo se ejecutó la inferencia.

## 6. Medidas de hardening aplicadas
- Mongo sin puerto publicado al exterior en Docker.
- API protegida por `X-API-Key`.
- CORS restringido a orígenes explícitos.
- Grafana sin acceso anónimo.
- TTL por defecto de 30 días para reducir retención innecesaria.

## 7. Lectura práctica
- si se busca máxima detección: mantener `0.05`;
- si se busca menos ruido operativo: revisar umbrales de `0.45` a `0.50`;
- si se necesita más detalle forense: activar explícitamente `STORE_MSG_ORIGINAL` y justificarlo.
