# Grafana MVP

Esta carpeta contiene provision automatica para paneles base de monitorizacion.

## Estructura
- `provisioning/datasources/datasource.yml`: datasource JSON hacia `http://api:8000`.
- `provisioning/dashboards/dashboard.yml`: registro de dashboards por archivo.
- `dashboards/tfg_mvp_dashboard.json`: dashboard MVP (6 paneles).

## Paneles previstos
- Volumen de mensajes.
- Proporcion benigno/amenaza.
- Latencia media y p95.
- Tasa de errores.
- Distribucion de `score_1`.
- Precision/recall por ejecucion.

## Nota de plugin
Se usa `marcusolsson-json-datasource`, instalado por `docker-compose`.
