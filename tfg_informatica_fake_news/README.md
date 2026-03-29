# TFG de Ingenieria Informatica - Deteccion Temprana de Fake News en Telegram

Este proyecto mantiene el foco en datos, preprocesamiento y logica de aplicacion. En el estado actual ya cubre:

1. extraccion de mensajes desde Telegram;
2. normalizacion y deteccion de idioma;
3. construccion de un dataset ficticio etiquetado con schema estable;
4. preparacion de scripts reproducibles para entrenamiento y evaluacion futura.

En esta entrega no se entrena todavia ningun modelo. La siguiente fase queda preparada para que, cuando dispongas del dataset real, solo haya que sustituir la fuente de datos y lanzar el pipeline.

## Diferencia respecto al TFG de Computadores

Este proyecto no se centra en API, dashboard, Grafana ni despliegue multi-servicio. El foco esta en:

- adquisicion de mensajes;
- limpieza y normalizacion del texto;
- tokenizacion;
- deteccion de idioma;
- construccion de dataset;
- preparacion del pipeline de entrenamiento y evaluacion.

## Estructura actual

- `telegram_extractor.py`: extractor de mensajes con Telethon.
- `preprocessing.py`: limpieza, tokenizacion y deteccion de idioma.
- `main.py`: pipeline de ejemplo con modo Telegram real o muestra local.
- `scripts/build_seed_dataset.py`: genera el dataset ficticio etiquetado.
- `scripts/validate_dataset.py`: valida schema, etiquetas y nulos.
- `scripts/train_baseline.py`: deja preparado el entrenamiento baseline con `scikit-learn`.
- `scripts/evaluate_baseline.py`: deja preparada la evaluacion posterior de un modelo persistido.
- `configs/training_config.json`: parametros por defecto para la fase de entrenamiento futura.
- `data/raw/`: entradas crudas y muestras.
- `data/processed/`: salidas preprocesadas.
- `data/labeled/`: dataset ficticio de trabajo.
- `docs/`: memoria y propuesta academica.
- `tests/`: pruebas unitarias y de dataset.

## Flujo minimo actual

1. Generar o refrescar datos de ejemplo:

```powershell
python main.py --use-sample
```

2. Construir el dataset ficticio etiquetado:

```powershell
python -m scripts.build_seed_dataset
```

3. Validar el dataset:

```powershell
python -m scripts.validate_dataset --input data/labeled/fake_news_seed.csv
```

4. Comprobar la configuracion del entrenamiento sin entrenar nada:

```powershell
python -m scripts.train_baseline --dry-run
python -m scripts.evaluate_baseline --dry-run
```

## Ejecucion con Telegram

1. Copia `.env.example` a `.env`.
2. Completa `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` y los canales.
3. Ejecuta:

```powershell
python main.py --channels canal_fake_1 canal_fake_2 --limit 20
```

## Dataset ficticio

El dataset semilla de esta entrega es deliberadamente ficticio y solo sirve para:

- validar la estructura futura del dataset real;
- probar scripts y rutas;
- dejar preparada la siguiente fase del proyecto.

No debe usarse para presentar resultados academicos finales ni para afirmar rendimiento de IA.

## Pruebas

```powershell
python -m pytest -q
```
