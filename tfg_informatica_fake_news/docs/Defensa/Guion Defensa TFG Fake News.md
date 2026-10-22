# Guion de defensa — TFG Ingeniería Informática

**Detección temprana de fake news en Telegram mediante análisis automatizado de mensajes**

- **Autor:** Álvaro Osuna Flores
- **Titulación:** Grado en Ingeniería Informática · ETSII · URJC
- **Tutora:** Liliana Patricia Santacruz Valencia · Curso 2025/2026
- **Duración objetivo:** 12–18 minutos
- **Presentación:** `Defensa TFG Fake News.dc.html` (18 diapositivas)

> **Enfoque diferencial:** este TFG es de **Informática** — el valor está en los **datos, el preprocesamiento y la metodología experimental reproducible**, no en la arquitectura de despliegue (eso es el TFG de Computadores). Si el tribunal pregunta por la diferencia entre ambos, es exactamente eso. Defiende el método: dato fiable → modelo simple e interpretable → análisis honesto → siguiente iteración.

---

## 1. Guion por minutos

| Minuto | Diapositiva | Qué decir (idea clave) |
|---:|---|---|
| 0:00–0:45 | 01 · Portada | Saludo, nombre, título. "Un trabajo centrado en datos y método experimental reproducible." |
| 0:45–2:00 | 02 · Agenda · 03 · Problema | Cuatro fases. El reto no es desplegar, es **tratar la información**: texto ruidoso → corpus limpio y evaluable. |
| 2:00–3:00 | 04 · Objetivos | Objetivo general (base experimental) + 6 específicos ya implementados. |
| 3:00–4:30 | 05 · Metodología · 06 · Pipeline | Cuatro fases reproducibles y los módulos del pipeline de datos. |
| 4:30–7:00 | 07 · Dataset · 08 · Inclusión/Exclusión | Corpus de 50.503 filas (53,5/46,5%). Qué entra, qué se descarta y por qué — todo versionado. |
| 7:00–8:30 | 09 · Preprocesamiento | Siete reglas de normalización + banderas de calidad. El antes/después. |
| 8:30–10:00 | 10 · Baseline · 11 · Comparación | TF-IDF + lineal; Linear SVC gana por macro F1 (0.9424 vs 0.9408). |
| 10:00–11:30 | 12 · Métricas · 13 · Matriz | 94,3% accuracy; pocos falsos positivos (220) por diseño. |
| 11:30–13:00 | 14 · Interpretabilidad · 15 · Errores | **Fuga de estilo**: "reuters/said" vs "video/hillary". Dos patrones de error. |
| 13:00–14:30 | 16 · Limitaciones · 17 · Conclusiones | Limitaciones como decisiones honestas + trabajo futuro hacia Telegram real. |
| 14:30–15:00 | 18 · Cierre | Agradecimiento y preguntas. |

---

## 2. Discurso ampliado por diapositiva

**01 · Portada.** Buenos días. Soy Álvaro Osuna Flores y defiendo mi TFG del Grado en Ingeniería Informática: detección temprana de fake news en Telegram mediante análisis automatizado de mensajes. A diferencia de mi otro TFG, este es un trabajo centrado en datos, preprocesamiento y metodología experimental reproducible. La tutora ha sido Liliana Patricia Santacruz Valencia.

**02 · Agenda.** El trabajo se organiza en cuatro fases que estructuran la defensa: construcción y validación del dataset; baseline reproducible con TF-IDF y clasificadores lineales; análisis de resultados, interpretabilidad y limitaciones; y mejoras futuras orientadas a Telegram. Antes veremos problema, objetivos y pipeline.

**03 · Problema y enfoque diferencial.** Telegram propaga bulos con gran velocidad. Pero el reto que abordo no es de despliegue, sino de tratamiento de la información: convertir texto no estructurado en una base de datos limpia, consistente y evaluable. Esa es la diferencia clave con mi TFG de Computadores: aquí el valor académico está en los datos, la metodología y la evaluación reproducible.

**04 · Objetivos.** El objetivo general es desarrollar una base experimental para estudiar la detección temprana de fake news, con foco en procesamiento textual, calidad del dataset y evaluación reproducible. De ahí salen seis específicos ya implementados: extracción trazable desde Telegram, pipeline de limpieza y detección de idioma, construcción de un dataset binario reproducible desde fuentes documentadas, validación previa, comparación de baselines lineales y persistencia de artefactos.

**05 · Metodología.** Cuatro fases encadenadas: construyo y valido el dataset; entreno un baseline y comparo modelos; analizo resultados, interpretabilidad y limitaciones; y defino mejoras futuras. Es un planteamiento experimental clásico: dato fiable, modelo simple y reproducible, análisis honesto, siguiente iteración.

**06 · Pipeline de datos.** El pipeline está modularizado. `telegram_extractor` adquiere mensajes con Telethon con reintentos. `preprocessing` limpia, tokeniza, detecta idioma y marca banderas de calidad. `dataset_manager` deduplica de forma persistente. `build_real_dataset` unifica las fuentes externas en un corpus canónico. `validate_dataset` comprueba schema y consistencia antes de entrenar. Y `train_baseline` y `evaluate_baseline` cierran el ciclo.

**07 · Fase 1 · Dataset.** El dataset real se genera unificando dos colecciones externas documentadas: un dataset de noticias —archive2— que aporta casi 45.000 filas, y el corpus LIAR de PolitiFact, del que conservo solo las etiquetas más nítidas: `false` y `pants-fire` como fake news, `true` como verificado. El resultado es un corpus binario de 50.503 filas, razonablemente balanceado: 53,5% fake news y 46,5% verificado o neutro. Todo trazado con un hash SHA-256.

**08 · Inclusión/Exclusión.** Una parte importante de la calidad son las decisiones de inclusión y exclusión, documentadas en la metadata. Excluyo `archive3` por completo, y de LIAR descarto las etiquetas ambiguas —half-true, mostly-true, barely-true— porque introducen ruido en un problema binario. También filas vacías. La idea: no basta con tener etiquetas; hay que caracterizar el corpus y justificar qué entra y qué no.

**09 · Preprocesamiento.** El corazón del trabajo. Siete reglas versionadas: decodifico HTML y minúsculas; URLs → `url`, menciones → `usuario`; conservo el término base de los hashtags; elimino emojis y no-latinos; compacto espacios y tokenizo con regex; filtro stopwords; y marco con banderas de calidad los textos vacíos, cortos o de idioma desconocido. El ejemplo muestra el antes y el después. Esta normalización es lo que hace el dataset reproducible.

**10 · Fase 2 · Baseline.** Elijo deliberadamente un baseline simple e interpretable: TF-IDF con n-gramas (1,2), 5.000 features, y dos clasificadores lineales candidatos —regresión logística y Linear SVC—, ambos con `class_weight=balanced`. Partición estratificada con 25% de holdout y semilla fija. Y una política conservadora: umbral de probabilidad 0.60 y de decisión 0.30 para reducir la sobredetección. Selección automática por macro F1.

**11 · Comparación.** Entreno sobre 37.877 filas y evalúo en holdout de 12.626. La comparación es ajustada: logística 94,08% de macro F1, Linear SVC 94,24%. La selección automática elige Linear SVC por un margen pequeño pero consistente. Lo relevante no es el ganador, sino que la comparación es reproducible y documentada.

**12 · Resultados · Métricas.** Mejor baseline (Linear SVC) sobre holdout: accuracy 94,26%, macro F1 0.9424, con precisión y recall macro equilibrados en torno al 94%. Por clase: para fake news, precisión alta 0.9660 con recall 0.9253; para verificado, al contrario, recall alto 0.9625 y precisión 0.9179. Cuando el modelo dice fake news, acierta mucho; a cambio deja escapar algunos casos. Coherente con el umbral conservador.

**13 · Matriz de confusión.** Lo confirma: de los realmente verificados, 5.648 bien y solo 220 falsos positivos. De los realmente fake, 6.253 detectados y 505 falsos negativos. Este desbalance —pocos falsos positivos, algo más de falsos negativos— es consecuencia directa y buscada del umbral conservador: prefiero no acusar de fake news a contenido legítimo, aunque escape algún caso dudoso.

**14 · Interpretabilidad.** Lo más interesante metodológicamente. Al ser lineal, inspecciono los términos más influyentes. Y aparece un hallazgo incómodo pero honesto: la clase verificado la empujan términos como `reuters`, `said`, `washington reuters` o `on wednesday`. La clase fake news, términos como `video`, `via`, `hillary`, `read more` o `featured image`. El baseline no solo aprende el contenido, sino el estilo editorial y la procedencia. Es una fuga de estilo que hay que reconocer.

**15 · Análisis de errores.** El análisis cualitativo confirma dos patrones. Los falsos positivos son frases políticas breves y asertivas del corpus LIAR que, aunque etiquetadas como verificado, suenan a titular. Los falsos negativos tienen rasgos periodísticos o estilo de agencia, factual y breve, incluso siendo fake news. Ambos apuntan a lo mismo: hay mezcla de señales léxicas entre fuentes, y el modelo lo aprende.

**16 · Limitaciones.** Soy transparente: el corpus procede de fuentes externas, no anotado específicamente para Telegram; existe fuga de estilo entre fuentes, sobre todo por marcas como Reuters; binarizar LIAR simplifica un problema con más matices; y la detección de idioma introduce ruido en textos cortos. Importante: la evaluación sobre el corpus completo da macro F1 0.9674, pero **no es generalización** —reutiliza el dataset de entrenamiento—, es solo verificación reproducible del pipeline.

**17 · Conclusiones.** El proyecto dispone ya de una base experimental completa: dataset real documentado, validación previa, baseline reproducible, comparación entre clasificadores y artefactos para el análisis. La memoria queda en cuatro fases sólidas. Y lo más importante: el siguiente salto de calidad no pasa por más infraestructura, sino por acercar el dataset y la validación al dominio real de Telegram, con un conjunto anotado propio, mejor separación por fuente y análisis de errores más fino.

**18 · Cierre.** Con esto termino. Muchas gracias por su atención; quedo a disposición del tribunal.

---

## 3. Posibles preguntas del tribunal

### Sobre los datos
- **¿Por qué binarizar LIAR y no usar las 6 clases?** El objetivo es un baseline binario fake/verificado; las etiquetas intermedias (half-true, etc.) añaden ruido y ambigüedad. Lo documento como decisión, y queda como línea futura tratar el matiz.
- **¿El dataset está balanceado?** Sí, razonablemente: 53,5% fake / 46,5% verificado. Además uso `class_weight=balanced` para no sesgar hacia la mayoritaria.
- **¿Cómo garantizas la reproducibilidad del dataset?** Construcción versionada (`build_real_dataset`), validación de schema (`validate_dataset`) y hash SHA-256 del corpus; semilla fija en la partición.

### Sobre el modelo
- **¿Por qué un modelo lineal y no un transformer?** Es un baseline: prioriza reproducibilidad e **interpretabilidad** sobre rendimiento máximo. Precisamente esa interpretabilidad permitió detectar la fuga de estilo. Modelos avanzados quedan para después de consolidar el baseline.
- **El 94% parece muy alto, ¿es fiable?** En holdout sí, pero con cautela: parte del poder predictivo viene del estilo editorial y la procedencia de las fuentes, no solo del contenido. Por eso no lo presento como detección robusta final.
- **¿Por qué el umbral conservador (0.60 / 0.30)?** Para reducir falsos positivos: prefiero no acusar de fake news a contenido legítimo. La matriz lo confirma (220 FP frente a 505 FN).

### Metodológicas / de mejora
- **¿Cuál es la diferencia con tu TFG de Computadores?** Aquel es de sistema, integración y despliegue (arquitectura, API operacional, observabilidad). Este es de datos, lenguaje y método: dataset, preprocesamiento y evaluación reproducible.
- **¿Qué harías para llevarlo a producción real?** Construir un dataset propio anotado de Telegram, separar por fuente y tiempo para eliminar la fuga de estilo, análisis de errores más fino y calibración antes de probar modelos más complejos.
- **¿Qué es exactamente la "fuga de estilo"?** Que el modelo aprende a distinguir la fuente (p. ej. el estilo de agencia "Reuters") en lugar de la veracidad del contenido. Infla las métricas y limita la generalización.

---

## 4. Datos clave para memorizar
- Corpus: **50.503** filas · **53,5%** fake / **46,5%** verificado · idioma dominante `en` (50.421).
- Fuentes: **archive2** (44.898) + **LIAR/PolitiFact** (5.605).
- Baseline: TF-IDF (1,2)-gramas, 5.000 features · Logistic Regression vs **Linear SVC** (ganador).
- Resultados (holdout 12.626): **accuracy 94,26%**, **macro F1 0.9424**.
- Matriz: 5.648 VN · **220 FP** · **505 FN** · 6.253 VP.
- Cautela: macro F1 0.9674 sobre corpus completo = verificación del pipeline, **no** generalización.
