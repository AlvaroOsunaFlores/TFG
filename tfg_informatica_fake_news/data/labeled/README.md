# Dataset Ficticio

Esta carpeta contiene un dataset semilla ficticio para preparar la siguiente fase del TFG.

- No es un dataset academico definitivo.
- No debe usarse para extraer conclusiones finales sobre rendimiento de modelos.
- Su unica funcion es validar la estructura del dataset, los scripts y el flujo futuro de entrenamiento y evaluacion.

El archivo principal es `fake_news_seed.csv` y sigue esta schema:

- `source_id`
- `channel`
- `date_utc`
- `text`
- `normalized_text`
- `language`
- `label`
- `label_name`
- `source`

Etiquetas:

- `0`: `verificado_o_neutro`
- `1`: `fake_news`
