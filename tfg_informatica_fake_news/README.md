# TFG de Ingenieria Informatica - Deteccion temprana de fake news en Telegram

Este proyecto mantiene el foco academico en datos, preprocesamiento, dataset y experimentacion reproducible. No pretende desplegar una plataforma operativa completa, sino construir una base metodologica clara para estudiar clasificacion de contenido dudoso a partir de mensajes y textos cercanos al contexto Telegram.

El trabajo queda organizado en cuatro fases:

1. construccion y validacion del dataset;
2. baseline reproducible con TF-IDF y clasificadores lineales;
3. analisis de resultados y limitaciones;
4. mejoras futuras orientadas a Telegram.

## Alcance frente al TFG de Computadores

Aqui no se trabaja cola, API operacional, observabilidad ni despliegue distribuido. El valor academico del TFG de Informatica esta en:

- adquisicion y trazabilidad de datos;
- limpieza y normalizacion textual;
- control de calidad y consistencia del dataset;
- entrenamiento reproducible;
- comparacion de baselines;
- analisis de errores e interpretabilidad.

## Estructura principal

- `telegram_extractor.py`: extraccion desde Telegram con reintentos y reporte de canales fallidos.
- `preprocessing.py`: limpieza, tokenizacion, deteccion de idioma y banderas de calidad.
- `dataset_manager.py`: deduplicacion persistente de mensajes crudos.
- `pipeline.py`: orquestacion reproducible del flujo de datos.
- `scripts/build_real_dataset.py`: unifica datasets externos y genera el corpus canonico comprimido.
- `scripts/validate_dataset.py`: valida schema, etiquetas y consistencia minima.
- `scripts/train_baseline.py`: compara baselines lineales, selecciona el mejor por `macro_f1` y persiste artefactos.
- `scripts/evaluate_baseline.py`: evalua un modelo persistido y versiona salidas reproducibles.
- `configs/training_config.json`: configuracion por defecto del baseline.
- `reports/`: manifiestos, matrices de confusion, ejemplos de aciertos/errores y terminos influyentes.
- `docs/MEMORIA_TFG_ETSII_APA7.md`: memoria editable en Markdown.

## Fase 1. Construccion y validacion del dataset

El dataset real actual se genera en `data/labeled/fake_news_unified.csv.gz` a partir de:

- `archive2.zip`: `Fake.csv -> fake_news`, `True.csv -> verificado_o_neutro`.
- `archive.zip` (LIAR): `false -> fake_news`, `pants-fire -> fake_news`, `true -> verificado_o_neutro`.

Se excluyen de forma explicita:

- `archive3.zip`;
- las etiquetas `half-true`, `mostly-true` y `barely-true` de LIAR;
- filas vacias durante la reconstruccion.

Estado del dataset regenerado el `2026-04-09`:

- `50503` filas totales.
- Distribucion de etiquetas: `23470` verificado o neutro y `27033` fake news.
- Distribucion por fuente: `44898` filas de `archive2_news_dataset` y `5605` de `liar_politifact`.
- Idioma detectado dominante: `en` en `50421` filas; el resto son casos aislados producidos por textos cortos o ruidosos.
- Longitud media del texto crudo: `2278.58` caracteres.
- Longitud media de `normalized_text`: `374.76` tokens.

Las reglas de limpieza reales quedan documentadas en la metadata generada:

- minusculas y decodificacion HTML;
- reemplazo de URLs por `url`;
- reemplazo de menciones por `usuario`;
- preservacion del termino base de hashtags;
- eliminacion de emojis y caracteres fuera de la clase latina definida;
- filtrado de stopwords configurable;
- marcado de textos vacios, demasiado cortos o de idioma desconocido.

Comandos de reproduccion:

```powershell
python -m scripts.build_real_dataset
python -m scripts.validate_dataset --input data/labeled/fake_news_unified.csv.gz
```

La metadata ampliada se guarda en `data/labeled/fake_news_unified.metadata.json`.

## Fase 2. Baseline reproducible

El baseline actual trabaja con:

- `TfidfVectorizer` con n-gramas `(1, 2)` y `max_features=5000`;
- `LogisticRegression` y `LinearSVC` como candidatos;
- `class_weight="balanced"` en ambos clasificadores;
- `test_size=0.25`;
- politica de decision conservadora para reducir falsos positivos:
  - `probability_threshold = 0.60`
  - `decision_threshold = 0.30`
- seleccion automatica por `macro_f1`.

Entrenamiento regenerado el `2026-04-11`:

- run: `baseline-20260411T145313Z-a9ea359a`
- filas de entrenamiento: `37877`
- filas holdout: `12626`
- mejor modelo: `linear_svc`

Comparativa de candidatos en holdout:

| Modelo | Accuracy | Macro F1 |
| --- | ---: | ---: |
| Logistic Regression | 0.9410 | 0.9408 |
| Linear SVC | 0.9426 | 0.9424 |

Metricas del mejor modelo en holdout:

- `accuracy = 0.9426`
- `precision_macro = 0.9420`
- `recall_macro = 0.9439`
- `macro_f1 = 0.9424`
- `weighted_f1 = 0.9426`

Desglose por clase en holdout:

- `verificado_o_neutro`: precision `0.9179`, recall `0.9625`, f1 `0.9397`
- `fake_news`: precision `0.9660`, recall `0.9253`, f1 `0.9452`

Comando de reproduccion:

```powershell
python -m scripts.train_baseline
```

Artefactos generados por run:

- `training_manifest.json`
- `comparison.json`
- `classification_report.json`
- `holdout_predictions.csv`
- `confusion_matrix.json`
- `prediction_examples.json`
- `linear_model_terms.json`

## Fase 3. Analisis de resultados y limitaciones

La matriz de confusion del holdout del mejor baseline es:

| Real \\ Predicho | Verificado o neutro | Fake news |
| --- | ---: | ---: |
| Verificado o neutro | 5648 | 220 |
| Fake news | 505 | 6253 |

Lectura rapida:

- el umbral conservador reduce los falsos positivos de la clase `fake_news` y acepta mas falsos negativos;
- en este run hay `220` falsos positivos frente a `505` falsos negativos;
- la precision de `fake_news` sube a `0.9660`, mientras su recall baja a `0.9253`;
- el comportamiento es razonable para un baseline lineal, pero no debe confundirse con una validacion final sobre Telegram real.

El analisis cualitativo de `prediction_examples.json` deja dos patrones claros:

- los falsos positivos proceden sobre todo de frases politicas breves y muy asertivas del corpus LIAR, aunque su etiqueta original se haya mapeado a `verificado_o_neutro`;
- varios falsos negativos contienen marcas periodisticas y estilo de agencia, incluso cuando la etiqueta final es `fake_news`, lo que sugiere mezcla de senales lexicas entre fuentes.

La interpretabilidad se apoya en `linear_model_terms.json`. Para la regresion logistica, los terminos mas asociados a `verificado_o_neutro` son `reuters`, `said`, `washington reuters` y expresiones temporales como `on wednesday` o `on tuesday`. En sentido contrario, `fake_news` queda empujada por terminos como `video`, `via`, `hillary`, `read more` o `featured image`.

Esto revela una limitacion metodologica importante: parte del poder predictivo del baseline viene del estilo editorial y de la procedencia de las fuentes, no solo del contenido semantico. Por eso el baseline actual sirve como punto de partida reproducible, pero no como evidencia definitiva de deteccion robusta en canales reales de Telegram. La politica de umbral actual esta elegida deliberadamente para que el TFG de Informatica sea mas flexible que el de Computadores al etiquetar positivos: prefiere evitar sobredeteccion de `fake_news` aunque eso implique dejar escapar mas casos dudosos.

La evaluacion reproducida sobre el corpus completo (`evaluation-20260411T145543Z-521b0d3d`) arroja `macro_f1 = 0.9674`, pero esa cifra debe interpretarse como un artefacto de verificacion reproducible sobre el dataset cargado, no como estimacion independiente de generalizacion, ya que reutiliza el mismo corpus sobre el que se entreno el modelo persistido.

## Fase 4. Mejoras futuras

Las siguientes mejoras son las que mas valor aportarian a la memoria:

1. crear un conjunto etiquetado especifico de Telegram con criterio de anotacion trazable;
2. separar mejor por fuente y periodo temporal para reducir fugas de estilo entre train y test;
3. ampliar el analisis de errores por fuente, tema y longitud del mensaje;
4. estudiar calibracion, explicaciones locales y modelos mas avanzados como siguiente fase, no como sustitucion del baseline reproducible;
5. medir adaptacion real a Telegram, no solo rendimiento sobre corpus externos.

## Ejecucion minima

```powershell
python main.py --use-sample
python -m scripts.validate_dataset --input data/labeled/fake_news_unified.csv.gz
python -m scripts.train_baseline
python -m scripts.evaluate_baseline --manifest reports/training_runs/<run_id>/training_manifest.json
python -m pytest -q
```
