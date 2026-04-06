# Datasets Etiquetados

Esta carpeta contiene dos datasets con objetivos distintos:

- `fake_news_unified.csv.gz`: dataset real unificado para entrenamiento baseline.
- `fake_news_unified.metadata.json`: metadata reproducible del dataset real.
- `fake_news_seed.csv`: dataset semilla ficticio para smoke tests y regresion ligera.

## Dataset real

El dataset principal combina:

- `archive2.zip` con `Fake.csv` y `True.csv`;
- `archive.zip` (LIAR) usando solo `true`, `false` y `pants-fire`.

Se excluye `archive3.zip` por calidad metodologica.

## Schema canonico

Todos los ficheros etiquetados siguen esta schema base:

- `source_id`
- `channel`
- `date_utc`
- `text`
- `normalized_text`
- `language`
- `label`
- `label_name`
- `source`

Y el dataset real anade:

- `dataset_name`
- `dataset_split`
- `original_label`
- `title`
- `topic`

Etiquetas:

- `0`: `verificado_o_neutro`
- `1`: `fake_news`

## Nota de uso

- El dataset real sirve para entrenamiento reproducible de baseline.
- El dataset semilla ficticio se conserva solo para pruebas locales y smoke checks.
