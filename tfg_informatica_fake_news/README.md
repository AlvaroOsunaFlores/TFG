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
- `scripts/build_real_dataset.py`: unifica datasets reales externos y produce el corpus canonico comprimido.
- `scripts/build_seed_dataset.py`: genera el dataset ficticio etiquetado.
- `scripts/validate_dataset.py`: valida schema, etiquetas y nulos.
- `scripts/train_baseline.py`: entrena baselines y persiste manifiestos reproducibles.
- `scripts/evaluate_baseline.py`: evalua modelos persistidos y versiona resultados.
- `configs/training_config.json`: parametros por defecto de entrenamiento.
- `data/raw/`: entradas crudas, registro de deduplicacion y muestras.
- `data/processed/`: salidas preprocesadas.
- `data/labeled/`: dataset real versionado y dataset semilla de smoke.
- `models/`: salida de pipelines entrenados.
- `reports/`: artefactos de pipeline, entrenamiento y evaluacion.
- `tests/`: pruebas unitarias, de dataset y de scripts.
- `.github/workflows/ci.yml`: validacion automatica en GitHub Actions.

## Flujo minimo actual

1. Generar o refrescar datos de ejemplo:

```powershell
python main.py --use-sample
```

2. Validar el dataset real incluido en el repositorio:

```powershell
python -m scripts.validate_dataset --input data/labeled/fake_news_unified.csv.gz
```

3. Comprobar entrenamiento y evaluacion:

```powershell
python -m scripts.train_baseline --dry-run
python -m scripts.evaluate_baseline --dry-run
```

4. Ejecutar un entrenamiento baseline real:

```powershell
python -m scripts.train_baseline
```

5. Evaluar un modelo ya entrenado usando su manifest:

```powershell
python -m scripts.evaluate_baseline --manifest reports/training_runs/<run_id>/training_manifest.json
```

## Reconstruccion del dataset real

El baseline actual entrena sobre `data/labeled/fake_news_unified.csv.gz`, que se genera a partir de:

- `archive2.zip`: `Fake.csv -> fake_news`, `True.csv -> verificado_o_neutro`;
- `archive.zip` (LIAR): `true -> verificado_o_neutro`, `false -> fake_news`, `pants-fire -> fake_news`.

Se descartan `half-true`, `mostly-true` y `barely-true` para no forzar una binarizacion metodologicamente debil. Tambien se excluye `archive3.zip`.

Si necesitas reconstruir el dataset real desde los ZIP locales:

```powershell
python -m scripts.build_real_dataset --source-root ..\..\..\datos_entrenamiento\tfg_informatica_fake_news
```

`build_seed_dataset.py` se mantiene solo como utilidad secundaria para smoke tests y regresion ligera.

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

## Nota metodologica

El dataset real actual sirve para entrenamiento reproducible de baseline sobre colecciones publicas externas. No sustituye una fase experimental final especifica de Telegram ni debe usarse sin contexto para afirmar validez cientifica definitiva sobre desinformacion en canales reales.

## Pruebas

```powershell
python -m pytest -q
```
