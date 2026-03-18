# TFG de Ingenieria Informatica - Deteccion Temprana de Fake News en Telegram

Este proyecto arranca desde cero, aunque toma como inspiracion la experiencia del TFG de phishing. En esta primera fase se implementan solo los objetivos especificos 1 y 2:

1. extraer mensajes desde canales y grupos de Telegram usando su API;
2. normalizar los mensajes mediante un pipeline de preprocesamiento textual.

## Diferencia respecto al TFG de Computadores

Este proyecto no se centra todavia en API, dashboard, Grafana o despliegue. El foco esta en:

- adquisicion de mensajes;
- limpieza y normalizacion del texto;
- tokenizacion;
- deteccion de idioma;
- preparacion de una base reutilizable para dataset, entrenamiento y evaluacion.

## Estructura minima

- `telegram_extractor.py`: extractor de mensajes con Telethon.
- `preprocessing.py`: limpieza, tokenizacion y deteccion de idioma.
- `main.py`: pipeline de ejemplo con modo API real o modo muestra.
- `data/raw/`: entradas crudas y muestras.
- `data/processed/`: salidas preprocesadas.
- `docs/`: propuesta academica inicial.
- `tests/`: pruebas de humo y unitarias.

## Ejecucion minima con muestra

```powershell
python main.py --use-sample
```

Salida esperada:

- `data/raw/extracted_messages.json`
- `data/processed/preprocessed_messages.json`

## Ejecucion con Telegram

1. Copia `.env.example` a `.env`.
2. Completa `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` y los canales.
3. Ejecuta:

```powershell
python main.py --channels canal_fake_1 canal_fake_2 --limit 20
```

## Pruebas

```powershell
python -m pytest -q
```
