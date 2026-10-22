# Cambio 10 — Conclusiones y trabajo futuro

## Objetivo

Reescribir de forma conservadora el capítulo final para eliminar repeticiones, responder a los objetivos y presentar con precisión las contribuciones, el resultado, las limitaciones y la continuidad del trabajo.

## Extensión y estructura

Limitar el capítulo a unas tres páginas como máximo, respetando la maquetación actual. Organizarlo en este orden:

1. grado de cumplimiento del objetivo general;
2. contribuciones principales;
3. resultado experimental más relevante;
4. limitaciones y alcance real;
5. líneas de trabajo futuro.

Eliminar párrafos duplicados, conclusiones intermedias repetidas y resúmenes extensos de capítulos ya explicados.

## Apertura obligatoria

Comenzar con este párrafo:

> El presente Trabajo Fin de Grado ha permitido alcanzar el objetivo general de diseñar, implementar y evaluar una metodología experimental reproducible para la clasificación automática de fake news a partir de contenido textual. La solución integra la construcción y validación de un corpus binario, el preprocesamiento determinista de los textos, el entrenamiento de modelos supervisados, la evaluación mediante métricas de clasificación y la persistencia de los artefactos necesarios para reproducir y auditar los resultados.

## Contribuciones que deben sintetizarse

- construcción documentada del corpus binario unificado;
- reglas explícitas de inclusión, exclusión y transformación de etiquetas;
- preprocesamiento determinista y validaciones previas;
- comparación reproducible de dos modelos lineales con TF-IDF;
- persistencia de métricas, predicciones, matrices y artefactos de análisis;
- módulo independiente de adquisición desde Telegram para futuras extensiones.

## Resultado principal

Usar exactamente esta formulación:

> Linear SVC obtuvo el mejor resultado de los dos modelos comparados en la partición utilizada, con un macro F1 de 0,9424.

Explicar inmediatamente que el rendimiento puede estar influido por la fuente, el formato y el estilo editorial del corpus, por lo que no demuestra una capacidad general de detección.

## Limitaciones obligatorias

Resumir, sin ocultarlas:

- dependencia de datasets externos y de sus decisiones de etiquetado;
- posible aprendizaje de señales de procedencia o estilo editorial;
- simplificación derivada de la binarización;
- evaluación sobre la partición documentada;
- ausencia de un corpus anotado específicamente para Telegram;
- falta de validación de transferencia a nuevos dominios.

## Trabajo futuro

Priorizar líneas coherentes con las limitaciones:

- construir y anotar un corpus específico de mensajes de Telegram;
- definir un protocolo de selección, anotación y control de calidad;
- realizar evaluaciones de transferencia de dominio y particiones por fuente o periodo;
- ampliar el análisis de errores, calibración y explicabilidad;
- comparar modelos más avanzados solo después de consolidar una evaluación adecuada del dominio.

## Estilo

- Usar redacción académica impersonal o en tercera persona.
- Eliminar instrucciones al lector o al autor como `Use...`, `Manténgase...` o formulaciones imperativas similares.
- Evitar expresiones promocionales o absolutas.
- No introducir cifras nuevas ni repetir todas las tablas de evaluación.

## Prohibiciones

- No afirmar que se ha validado la detección en Telegram.
- No presentar el modelo como solución general o lista para producción.
- No afirmar generalización, robustez o despliegue sin evidencia.
- No comparar el TFG con el de Computers.

## Comprobaciones

- Cada objetivo específico tiene una respuesta breve y verificable.
- El resultado coincide con el resumen y el capítulo de evaluación.
- El trabajo futuro no se presenta como ya ejecutado.
- El capítulo no supera aproximadamente tres páginas y no contiene bloques repetidos.
