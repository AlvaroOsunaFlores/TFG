ESCUELA TECNICA SUPERIOR DE INGENIERIA INFORMATICA

DOBLE GRADO EN INGENIERIA INFORMATICA E INGENIERIA DE COMPUTADORES

CURSO ACADEMICO 2024-2025

TRABAJO FIN DE GRADO

# DETECCION TEMPRANA DE FAKE NEWS EN TELEGRAM MEDIANTE ANALISIS AUTOMATIZADO DE MENSAJES

Autor: Alvaro Osuna Flores

Tutora: Liliana Patricia Santacruz Valencia

## Resumen

El TFG de Ingenieria Informatica se plantea como un trabajo centrado en datos, preprocesamiento y metodologia experimental reproducible. El objetivo no es desplegar una arquitectura multiservicio, sino construir una base tecnica que permita recopilar mensajes, normalizar texto, consolidar un dataset util y entrenar un baseline interpretable con artefactos trazables. En su estado actual, el proyecto ya no se limita a preparar scripts para un trabajo futuro: incluye la generacion de un dataset real unificado, su validacion, el entrenamiento de baselines lineales, la comparacion de modelos, la persistencia de matrices de confusion y la extraccion de ejemplos de aciertos y errores.

## 1. Introduccion

Telegram facilita la difusion rapida de contenidos y, con ello, la propagacion de bulos, cadenas alarmistas y mensajes politicamente polarizados. Ese contexto justifica la necesidad de construir una base software que permita tratar el texto antes de plantear modelos mas complejos. El interes academico de este TFG esta en ese proceso: adquisicion de datos, limpieza, consistencia del dataset y evaluacion reproducible de un baseline de clasificacion.

## 2. Objetivo general

Desarrollar una base experimental para estudiar deteccion temprana de fake news con foco en procesamiento textual, calidad del dataset y evaluacion reproducible.

## 3. Objetivos especificos implementados

1. Implementar extraccion y trazabilidad de mensajes desde Telegram.
2. Disenar un pipeline de limpieza, tokenizacion y deteccion de idioma.
3. Construir un dataset binario reproducible a partir de fuentes externas documentadas.
4. Validar el dataset antes de entrenar.
5. Comparar baselines lineales bajo una configuracion reproducible.
6. Persistir artefactos utiles para memoria: metricas, matriz de confusion, ejemplos de aciertos y errores, y terminos influyentes.

## 4. Arquitectura funcional del proyecto

El trabajo se organiza en los siguientes bloques:

- `telegram_extractor.py` para la ingesta desde Telegram.
- `preprocessing.py` para limpieza, tokenizacion, deteccion de idioma y banderas de calidad.
- `dataset_manager.py` para deduplicacion persistente.
- `scripts/build_real_dataset.py` para construir el corpus etiquetado real.
- `scripts/validate_dataset.py` para comprobar schema y consistencia.
- `scripts/train_baseline.py` para entrenar, comparar y seleccionar el baseline.
- `scripts/evaluate_baseline.py` para evaluar un modelo persistido y regenerar artefactos de analisis.

Esta arquitectura deja clara la separacion del TFG de Computadores: aqui el valor esta en el tratamiento de la informacion y en la metodologia experimental, no en el despliegue operativo del sistema.

## 5. Fase 1. Construccion y validacion del dataset

El dataset actual se genera en `data/labeled/fake_news_unified.csv.gz` a partir de dos colecciones externas:

- `archive2.zip`, con noticias etiquetadas como `Fake` y `True`;
- `archive.zip` (LIAR), del que solo se conservan `false`, `pants-fire` y `true`.

Se descartan explicitamente:

- `archive3.zip`;
- las etiquetas `half-true`, `mostly-true` y `barely-true` de LIAR;
- filas vacias durante la reconstruccion.

La regeneracion realizada el `2026-04-09` produce el siguiente resumen:

- `50503` filas totales.
- `23470` filas `verificado_o_neutro`.
- `27033` filas `fake_news`.
- `44898` filas procedentes de `archive2_news_dataset`.
- `5605` filas procedentes de `liar_politifact`.

La metadata ampliada incluye informacion adicional relevante para memoria:

- distribucion de idiomas detectados;
- idiomas incluidos;
- resumen de longitud del texto crudo y del texto normalizado;
- reglas reales de limpieza aplicadas por `preprocessing.py`;
- reglas de exclusion empleadas al construir el corpus.

El idioma detectado dominante es `en` en `50421` filas. El resto de idiomas aparece en cantidades muy pequenas y debe interpretarse como ruido esperable de deteccion automatica sobre textos cortos, titulares o contenido parcialmente degradado. La longitud media del texto crudo es `2278.58` caracteres y la de `normalized_text` es `374.76` tokens, con medianas de `2084` y `346`, respectivamente.

Las reglas de limpieza implementadas y versionadas en metadata son:

1. decodificacion HTML y paso a minusculas;
2. sustitucion de URLs por el token `url`;
3. sustitucion de menciones por `usuario`;
4. preservacion del termino base de hashtags;
5. eliminacion de emojis y caracteres fuera de la clase latina definida;
6. filtrado de stopwords configurable;
7. marcado de textos vacios, demasiado cortos o de idioma desconocido.

Esta fase responde al primer punto que la memoria necesita destacar: no solo existe una distribucion de etiquetas, sino tambien una caracterizacion minima del corpus, de su limpieza y de sus criterios de inclusion y exclusion.

## 6. Fase 2. Baseline reproducible con TF-IDF y clasificadores lineales

El entrenamiento baseline se apoya en `configs/training_config.json` y mantiene una configuracion deliberadamente simple:

- vectorizacion TF-IDF con n-gramas `(1, 2)`;
- `max_features = 5000`;
- candidatos `LogisticRegression` y `LinearSVC`;
- `class_weight = "balanced"` en ambos modelos;
- particion `train/test` estratificada con `test_size = 0.25`;
- politica de decision conservadora para reducir falsos positivos:
  - `probability_threshold = 0.60`
  - `decision_threshold = 0.30`
- seleccion automatica por `macro_f1`.

La ejecucion reproducida el `2026-04-11` genera el run `baseline-20260411T145313Z-a9ea359a`, con `37877` filas de entrenamiento y `12626` filas holdout. La comparativa entre modelos es la siguiente:

| Modelo | Accuracy | Macro F1 |
| --- | ---: | ---: |
| Logistic Regression | 0.9410 | 0.9408 |
| Linear SVC | 0.9426 | 0.9424 |

Por tanto, el mejor baseline seleccionado es `linear_svc`.

Las metricas del modelo ganador sobre el holdout son:

- `accuracy = 0.9426`
- `precision_macro = 0.9420`
- `recall_macro = 0.9439`
- `macro_f1 = 0.9424`
- `weighted_f1 = 0.9426`

Desglosadas por clase:

- `verificado_o_neutro`: precision `0.9179`, recall `0.9625`, f1 `0.9397`;
- `fake_news`: precision `0.9660`, recall `0.9253`, f1 `0.9452`.

Ademas del modelo y las metricas agregadas, el script persiste:

- `comparison.json`
- `classification_report.json`
- `holdout_predictions.csv`
- `confusion_matrix.json`
- `prediction_examples.json`
- `linear_model_terms.json`
- `training_manifest.json`

Con ello, la memoria puede pasar de una simple descripcion de "entreno y metricas" a un analisis reproducible del comportamiento del baseline.

## 7. Fase 3. Analisis de resultados y limitaciones

La matriz de confusion del holdout del mejor baseline es:

| Real \\ Predicho | Verificado o neutro | Fake news |
| --- | ---: | ---: |
| Verificado o neutro | 5648 | 220 |
| Fake news | 505 | 6253 |

Este resultado refleja un cambio metodologico deliberado: el umbral de decision se ha desplazado para hacer el baseline de Informatica mas flexible que el de Computadores a la hora de marcar positivos. Eso reduce la sobredeteccion de `fake_news`, de modo que los falsos positivos bajan a `220`, mientras los falsos negativos suben a `505`.

Los ejemplos almacenados en `prediction_examples.json` permiten analizar errores concretos. Dos patrones aparecen de forma consistente:

1. varios falsos positivos pertenecen al corpus LIAR y son enunciados politicos cortos, asertivos y cargados lexicalmente, aunque su etiqueta mapeada sea `verificado_o_neutro`;
2. varios falsos negativos presentan rasgos periodisticos cercanos a agencia o un estilo factual breve, incluso cuando la etiqueta final es `fake_news`.

La interpretabilidad se refuerza con `linear_model_terms.json`. La regresion logistica, utilizada aqui como analisis complementario aunque no sea el mejor modelo, asigna pesos negativos muy altos a terminos como `reuters`, `said`, `washington reuters`, `on wednesday` o `on tuesday`, claramente asociados a `verificado_o_neutro`. En cambio, la clase `fake_news` queda empujada por terminos como `video`, `via`, `hillary`, `read more`, `featured image` o `president trump`.

Esta observacion es metodologicamente relevante: el baseline no solo aprende contenido semantico, sino tambien rasgos de estilo y procedencia editorial. Eso explica parte del rendimiento y obliga a interpretar las metricas con cautela. El modelo funciona como baseline reproducible, pero todavia no garantiza una deteccion robusta de desinformacion en Telegram real. Ademas, la politica actual favorece precision en la clase `fake_news` frente a recall, porque en este TFG interesa evitar etiquetados positivos excesivos.

La evaluacion regenerada en `evaluation-20260411T145543Z-521b0d3d` produce `macro_f1 = 0.9674` sobre el corpus completo cargado. Esa cifra es util como verificacion reproducible del pipeline de evaluacion, pero no debe presentarse como estimacion independiente de generalizacion porque reutiliza el mismo dataset sobre el que se entreno el modelo persistido.

Las limitaciones principales del estado actual son:

1. el corpus procede de fuentes externas y no de un conjunto anotado especificamente para Telegram;
2. existe posible fuga de estilo entre fuentes, especialmente por la presencia de marcas muy distintivas como `Reuters`;
3. la binarizacion de LIAR simplifica un problema originalmente mas rico en matices;
4. la deteccion automatica de idioma introduce una pequena cantidad de ruido en textos muy cortos o atipicos.

## 8. Fase 4. Mejoras futuras

Las lineas de continuidad mas coherentes para la memoria y para una futura ampliacion del proyecto son:

1. crear un dataset anotado especificamente sobre mensajes de Telegram;
2. controlar mejor la separacion por fuente y por periodo temporal para reducir fugas de estilo;
3. ampliar el analisis de errores por fuente, tema y longitud del mensaje;
4. estudiar explicabilidad local y calibracion sin abandonar el baseline reproducible como referencia;
5. explorar modelos mas avanzados solo despues de consolidar una validacion experimental especifica de Telegram.

## 9. Conclusion

El proyecto ya dispone de una base experimental completa para la fase actual del TFG: dataset real documentado, validacion previa, entrenamiento baseline reproducible, comparacion entre clasificadores lineales y artefactos suficientes para realizar analisis de resultados y limitaciones. Eso permite presentar la memoria con una estructura mas solida: fase de dataset, fase de baseline, fase de analisis y fase de mejoras futuras. El siguiente salto de calidad no pasa por desplegar mas infraestructura, sino por acercar el dataset y la validacion al dominio real de Telegram.
