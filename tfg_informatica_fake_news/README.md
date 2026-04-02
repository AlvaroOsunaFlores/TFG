# TFG de Ingenieria Informatica - Deteccion Temprana de Fake News en Telegram

Este proyecto mantiene el foco en tratamiento de la informacion, preprocesamiento, dataset y experimentacion reproducible. El valor academico del TFG no esta en desplegar una plataforma multiservicio, sino en preparar un pipeline de datos que permita:

1. extraer mensajes desde Telegram con trazabilidad de fallos;
2. deduplicar registros de manera persistente;
3. normalizar texto y medir calidad minima del contenido;
4. construir datasets consistentes;
5. entrenar y evaluar baselines con artefactos reproducibles.

## Diferencia respecto al TFG de Computadores

Este proyecto no se centra en cola, API operacional, Grafana ni despliegue distribuido. El foco esta en:

- adquisicion de mensajes;
- limpieza y normalizacion del texto;
- deteccion de idioma y control de calidad;
- deduplicacion y gestion de dataset;
- trazabilidad experimental;
- entrenamiento y evaluacion de modelos.

La extraccion desde Telegram se conserva como punto de entrada de datos, pero el valor academico del TFG esta en el tratamiento de la informacion y en la preparacion de una experimentacion reproducible sobre datasets y modelos.

## Estructura actual

- `telegram_extractor.py`: extractor con reporte de canales fallidos y reintentos basicos.
- `preprocessing.py`: limpieza, tokenizacion, filtrado basico de stopwords y banderas de calidad.
- `dataset_manager.py`: deduplicacion persistente y gestion de registros crudos.
- `pipeline.py`: orquestacion reproducible del flujo de datos.
- `main.py`: CLI principal con modo Telegram real o muestra local.
- `experiment_registry.py`: manifiestos y run IDs para entrenamiento/evaluacion.
- `scripts/build_seed_dataset.py`: genera el dataset ficticio etiquetado.
- `scripts/validate_dataset.py`: valida schema, etiquetas y nulos.
- `scripts/train_baseline.py`: entrena baselines y persiste manifiestos reproducibles.
- `scripts/evaluate_baseline.py`: evalua modelos persistidos y versiona resultados.
- `configs/training_config.json`: parametros por defecto de entrenamiento.
- `data/raw/`: entradas crudas, registro de deduplicacion y muestras.
- `data/processed/`: salidas preprocesadas.
- `data/labeled/`: dataset ficticio de trabajo.
- `models/`: salida de pipelines entrenados.
- `reports/`: artefactos de pipeline, entrenamiento y evaluacion.
- `tests/`: pruebas unitarias, de dataset y de scripts.
- `.github/workflows/ci.yml`: validacion automatica en GitHub Actions.

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

4. Comprobar entrenamiento y evaluacion:

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

El pipeline genera:

- datos crudos deduplicados en `data/raw/`;
- datos procesados en `data/processed/`;
- manifiesto del pipeline en `reports/pipeline_runs/`.

## Dataset ficticio

El dataset semilla de esta entrega es deliberadamente ficticio y solo sirve para:

- validar la estructura futura del dataset real;
- comprobar scripts, rutas y manifiestos;
- dejar preparada la siguiente fase experimental.

No debe usarse para presentar resultados academicos finales ni para afirmar rendimiento cientifico de IA sobre fake news reales.

## Pruebas

```powershell
python -m pytest -q
```
