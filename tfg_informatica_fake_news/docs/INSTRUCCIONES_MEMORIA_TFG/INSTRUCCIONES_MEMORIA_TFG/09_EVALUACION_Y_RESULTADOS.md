# Cambio 9 — Evaluación experimental y análisis de resultados

## Objetivo

Reencuadrar la evaluación para que las métricas se interpreten correctamente dentro del corpus utilizado, sin recalcular resultados ni extrapolarlos a Telegram u otros dominios.

## Título del capítulo

Usar:

> Evaluación experimental y análisis de resultados

## Apertura obligatoria

Al comienzo del capítulo, aclarar que:

- las métricas corresponden al corpus unificado construido a partir de archive2 y LIAR;
- la evaluación utiliza la partición ya documentada;
- los mensajes de Telegram no intervienen en el entrenamiento ni en la prueba;
- los resultados miden el rendimiento en ese marco experimental y no una generalización universal.

## Resultados que deben conservarse

No recalcular ni alterar:

- 50.503 registros en el corpus unificado;
- 23.470 registros de clase 0;
- 27.033 registros de clase 1 o *fake*;
- comparación de los dos modelos lineales documentados;
- Linear SVC como mejor modelo de los dos en la partición utilizada;
- macro F1 de 0,9424 para Linear SVC;
- tablas, matrices de confusión y figuras ya respaldadas por los artefactos existentes.

Usar esta formulación para el resultado principal:

> Linear SVC obtuvo el mejor resultado de los dos modelos comparados en la partición utilizada, con un macro F1 de 0,9424.

No sustituirla por “el mejor modelo”, “alta precisión general” o afirmaciones equivalentes más amplias.

## Interpretación de los umbrales

Si se mantienen los umbrales 0,60 y 0,30, describirlos como decisiones de diseño conservadoras orientadas a reducir falsos positivos o a reservar una zona de incertidumbre. Aclarar que:

- no fueron aprendidos automáticamente por el modelo;
- no son universales;
- no se validaron para todos los dominios;
- no constituyen por sí solos una garantía de fiabilidad.

## Pruebas automatizadas

Cuando los artefactos del proyecto sigan confirmándolo, documentar 16 pruebas superadas y 0 fallidas. Agrupar su explicación, sin inventar nombres o ejecuciones, en ámbitos como:

- preprocesamiento;
- construcción y validación del corpus;
- adquisición simulada desde Telegram;
- entrenamiento;
- evaluación y persistencia;
- análisis de resultados.

No presentar las pruebas unitarias como demostración de validez estadística o generalización.

## Sección 5.8

Renombrarla como:

> Interpretación y límites de validez

Incluir al menos:

- validez del baseline dentro del corpus y la partición usados;
- posible dependencia de la fuente, el estilo editorial y el formato;
- limitación de emplear una única partición, si así se hizo;
- ausencia de evaluación con mensajes de Telegram;
- necesidad de estudiar transferencia de dominio antes de un uso externo;
- utilidad del trabajo como referencia reproducible, no como detector general.

Reformular o eliminar propuestas de despliegue automático que no estén justificadas.

## Criterio de aceptación del experimento

Expresar que el baseline se acepta como referencia reproducible para el corpus evaluado. No afirmar que cumple un criterio de aceptación para cualquier noticia o plataforma.

## Qué conservar

- Métricas, tablas, figuras, fórmulas y análisis correctos.
- Orden interno siempre que sea compatible con el nuevo título y la nueva sección 5.8.
- Explicaciones de errores y términos influyentes respaldadas por los resultados existentes.

## Comprobaciones

- Todas las cifras coinciden entre texto, tablas, resumen y conclusiones.
- No aparece ninguna métrica atribuida a Telegram.
- Las limitaciones tienen peso suficiente y no quedan reducidas a una frase final.
- No se ha ejecutado ningún entrenamiento ni se ha modificado ningún resultado.
