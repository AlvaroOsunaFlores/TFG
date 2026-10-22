# Cambio 6 — Requisitos del sistema documental

## Objetivo

Reordenar los requisitos para que sigan el flujo real del experimento y reflejen la prioridad del corpus, la reproducibilidad y la evaluación. Telegram debe quedar como requisito complementario.

## Requisitos funcionales y orden obligatorio

Reformular los requisitos actuales manteniendo su información correcta y asignarles esta lógica:

- **RF1 — Construcción del corpus:** integrar los datasets públicos seleccionados en un corpus binario y documentar criterios, campos y transformación de etiquetas.
- **RF2 — Preprocesamiento:** aplicar de forma determinista la limpieza, normalización y preparación de los textos.
- **RF3 — Validación:** comprobar esquema, tipos, integridad, etiquetas válidas, nulos, duplicados y condiciones necesarias para entrenar.
- **RF4 — Entrenamiento:** entrenar los modelos lineales ya implementados a partir de representaciones TF-IDF y de la partición definida.
- **RF5 — Comparación y evaluación:** calcular y conservar las métricas, matrices y salidas que permiten comparar los modelos.
- **RF6 — Persistencia:** guardar configuración, métricas, predicciones y artefactos experimentales relevantes.
- **RF7 — Reproducción:** permitir repetir y auditar el proceso con los mismos datos, parámetros y condiciones documentadas.
- **RF8 — Adquisición opcional desde Telegram:** extraer mensajes bajo demanda como módulo independiente para apoyar la creación futura de corpus del dominio.

El RF8 no debe indicar que esos mensajes se incorporan automáticamente al corpus etiquetado ni que se clasifican dentro de la evaluación actual.

## Requisitos no funcionales

- Conservar los requisitos válidos sobre reproducibilidad, mantenibilidad, trazabilidad, robustez y documentación.
- Revisar sus identificadores tras la reordenación y actualizar todas las referencias cruzadas.
- Eliminar o reescribir el RNF5 actual si fundamenta la validez del trabajo en diferenciarse de un TFG de Computers.
- No crear requisitos de despliegue, tiempo real, escalabilidad o precisión general que no estén implementados y documentados.

## Trazabilidad

Para cada requisito, confirmar su correspondencia con:

- una sección de diseño o desarrollo;
- una evidencia documental o prueba existente, cuando proceda;
- una comprobación en el capítulo de evaluación, si es evaluable.

No inventar pruebas para completar la trazabilidad.

## Qué conservar

- El formato de las tablas o listas de requisitos.
- Criterios de validación ya presentes que sean correctos.
- Restricciones técnicas reales y verificables.

## Comprobaciones

- Numeración continua y sin referencias huérfanas.
- Orden de RF1 a RF8 coincidente con el flujo del pipeline.
- Telegram descrito como módulo opcional e independiente.
- Ninguna mención a comparaciones con otros TFG.
