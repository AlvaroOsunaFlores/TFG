# Grafana MVP

Esta carpeta contiene el provisioning del datasource y del dashboard base.

## Cambios de seguridad
- acceso anónimo desactivado;
- credenciales de administrador cargadas desde `.env`;
- datasource configurado para enviar `X-API-Key` a FastAPI.

## Estructura
- `provisioning/datasources/datasource.yml`: datasource JSON hacia `http://api:8000`.
- `provisioning/dashboards/dashboard.yml`: registro de dashboards.
- `dashboards/tfg_mvp_dashboard.json`: dashboard MVP.

## Paneles previstos
- volumen de mensajes;
- proporción benigno/amenaza;
- latencia media y p95;
- tasa de errores;
- distribución de `score_1`;
- métricas por ejecución.

## Nota
La fuente de verdad para métricas por ejecución está en la API y en `reports/runs/<run_id>/`.
