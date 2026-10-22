# Cambio 2 — Objetivo general y objetivos específicos

## Objetivo

Reformular los objetivos para que el centro del TFG sea la metodología experimental reproducible, la construcción del corpus y la evaluación de modelos TF-IDF, dejando Telegram como extensión complementaria.

## Objetivo general obligatorio

Incluir, sin alterar su significado:

> Diseñar, implementar y evaluar una metodología experimental reproducible para la clasificación automática de fake news a partir de información textual, mediante la construcción y validación de un corpus unificado y la comparación de modelos supervisados basados en TF-IDF.

Si la redacción institucional exige una adaptación mínima de puntuación o concordancia, conservar todos sus elementos sustantivos.

## Objetivos específicos y orden obligatorio

Redactarlos como acciones verificables y mantener este orden:

1. Construir un corpus binario unificado a partir de conjuntos de datos públicos, documentando los criterios de inclusión y exclusión y la transformación de las etiquetas.
2. Definir un proceso determinista de limpieza, normalización y representación de los textos.
3. Establecer validaciones automáticas del esquema, la integridad, las etiquetas, los valores nulos y los duplicados del corpus.
4. Entrenar y comparar modelos lineales supervisados basados en representaciones TF-IDF.
5. Evaluar los modelos mediante métricas de clasificación y analizar los errores y los términos influyentes.
6. Persistir la configuración, las métricas, las predicciones, las matrices de confusión y los artefactos necesarios para reproducir y auditar los experimentos.
7. Incorporar, como extensión complementaria, un módulo de extracción bajo demanda desde Telegram para facilitar la creación futura de corpus del dominio.

## Cambios de coherencia

- Alinear con estos objetivos el resumen, la introducción, los requisitos, la evaluación y las conclusiones.
- Eliminar cualquier objetivo que consista en diferenciar el trabajo respecto a un TFG de Computers.
- Evitar objetivos que prometan detección general, despliegue real o evaluación en Telegram.
- No añadir objetivos que no estén respaldados por el contenido existente.

## Qué conservar

- La ubicación actual de la sección y su nivel de encabezado.
- El formato de lista y la numeración del documento.
- Las explicaciones válidas sobre reproducibilidad, corpus, preprocesamiento, modelos y evaluación.

## Comprobaciones

- Cada objetivo específico debe tener correspondencia explícita con al menos una sección posterior.
- Ningún objetivo debe afirmar que los mensajes de Telegram forman parte del corpus de entrenamiento o prueba.
- El objetivo general debe reaparecer de manera coherente, no necesariamente literal, en la conclusión.
