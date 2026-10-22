# Cambio 7 — Arquitectura y Figura 1

## Objetivo

Corregir la arquitectura conceptual para separar con claridad la ruta experimental evaluada y la ruta complementaria de adquisición desde Telegram.

## Figura 1: contenido obligatorio

Redibujar la Figura 1 manteniendo, en la medida de lo posible, su estilo visual, dimensiones, colores, tipografía, posición y calidad. Debe mostrar dos rutas independientes.

### Ruta experimental evaluada

`archive2 + LIAR → corpus unificado → validación → preprocesamiento → TF-IDF → modelos → evaluación y artefactos`

### Ruta complementaria

`Telegram → extracción → deduplicación → preprocesamiento → mensajes sin etiquetar / futuro corpus`

No incluir ninguna flecha que indique que Telegram alimentó el corpus, el entrenamiento o la evaluación actuales.

## Texto que acompaña a la figura

Actualizar los párrafos inmediatamente anteriores y posteriores para explicar:

- qué componentes forman la ruta evaluada;
- qué artefactos se guardan para facilitar la reproducibilidad;
- que la ruta de Telegram es independiente y produce mensajes sin etiquetar;
- que una futura integración requeriría un protocolo de selección, anotación y validación del corpus.

## Pie y nota de la figura

- Mantener la numeración como Figura 1 salvo que la numeración automática determine otra cosa.
- Usar número en negrita y título en cursiva, de acuerdo con el documento.
- Corregir cualquier salto que divida la palabra `Nota.` en líneas o páginas distintas.
- Incluir una nota breve que aclare que solo la primera ruta sustenta los resultados experimentales de la memoria.
- Añadir fuente únicamente si la figura reutiliza material externo. Si es elaboración propia, usar la fórmula coherente con la guía institucional y con el resto del documento.

## Qué conservar

- El enfoque gráfico general y la posición de la figura.
- Los nombres técnicos ya consolidados, siempre que no creen una relación falsa.
- La explicación válida de los componentes internos.

## Prohibiciones

- No representar Telegram como entrada del entrenamiento actual.
- No añadir servicios, modelos o etapas que no existan.
- No sustituir la figura por una imagen de estilo radicalmente distinto.

## Comprobaciones

- La figura se entiende al imprimirse y no tiene texto cortado o ilegible.
- Se cita en el cuerpo antes de aparecer.
- El pie, la nota y la figura permanecen juntos en la misma página cuando sea razonablemente posible.
- Las dos rutas quedan visualmente separadas y sin flechas ambiguas.
