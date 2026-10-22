# Cambio 8 — Desarrollo y módulo complementario de Telegram

## Objetivo

Revisar el capítulo de desarrollo para presentar Telegram como un módulo de adquisición independiente, sin atribuirle participación en el entrenamiento ni una validación real no demostrada.

## Cambio de título

Renombrar la sección 4.4 como:

> Módulo complementario de adquisición desde Telegram

Si la numeración cambia al actualizar campos, conservar el título y usar la numeración automática resultante.

## Contenido obligatorio

La sección debe indicar de manera inequívoca que:

- el entrenamiento y la evaluación utilizan los datasets públicos etiquetados descritos en la memoria;
- los mensajes extraídos de Telegram no se utilizaron en esos experimentos;
- el módulo permite adquirir, normalizar y deduplicar mensajes bajo demanda;
- su salida permanece sin etiquetar y podría apoyar la construcción futura de un corpus del dominio;
- cualquier uso experimental posterior requeriría selección, anotación, control de calidad y un protocolo de evaluación específico.

## Validación y pruebas del módulo

La evidencia disponible indica que las pruebas de Telegram emplean un cliente simulado. Redactar la validación de forma fiel a esa evidencia:

- describir las pruebas como pruebas automatizadas o simuladas del comportamiento del módulo;
- no afirmar que se verificó el acceso real a canales o conversaciones si no existe una evidencia explícita en la documentación de referencia;
- no afirmar operación continua, monitorización en producción ni cumplimiento de rendimiento real;
- distinguir claramente entre implementación, prueba simulada y validación en un entorno real.

## Qué conservar

- Detalles técnicos existentes sobre extracción, normalización, deduplicación y tratamiento de mensajes que sean correctos.
- Diagramas, tablas o fragmentos explicativos útiles, corrigiendo solo su alcance.
- El orden general del capítulo y su estilo de redacción.

## Prohibiciones

- No modificar el código para hacer coincidir la memoria.
- No añadir capturas o resultados inventados de Telegram.
- No presentar el módulo como origen del corpus etiquetado.
- No usar expresiones que impliquen detección automática de fake news en Telegram.

## Comprobaciones

- Todas las menciones a Telegram en desarrollo son coherentes con la Figura 1 y con la evaluación.
- La conclusión no atribuye al módulo resultados que pertenecen al corpus público.
- Las pruebas simuladas están identificadas como tales.
