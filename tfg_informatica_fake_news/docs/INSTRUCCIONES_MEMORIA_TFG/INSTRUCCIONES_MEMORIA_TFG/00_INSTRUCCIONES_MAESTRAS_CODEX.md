# Instrucciones maestras para revisar únicamente la memoria del TFG

## Objetivo

Revisar la memoria del TFG de Álvaro Osuna Flores aplicando **solo** los cambios documentales indicados por la tutora y descritos en los archivos `01` a `13` de este paquete. El trabajo se limita al documento académico: no se debe modificar código, pruebas, datos, modelos, configuraciones, repositorios ni resultados experimentales.

## Documento de entrada y copias de seguridad

1. Descomprimir el ZIP conservando su estructura.
2. Localizar la memoria en `tfg_informatica_fake_news/docs/TFG_GII_Alvaro_Osuna_Flores_Deteccion_Fake_News_Telegram_Memoria.docx`.
3. No sobrescribir el archivo original. Crear primero una copia de trabajo.
4. Usar como nombre de salida:
   - `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.docx`
   - `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.pdf`
5. Crear además `CAMBIOS_REALIZADOS.md`, con una relación breve y verificable de los cambios efectuados, las fuentes consultadas y cualquier cuestión pendiente.

## Jerarquía de fuentes

Resolver cualquier conflicto siguiendo este orden:

1. Indicaciones expresas de la tutora incluidas en estos archivos.
2. Archivos de la carpeta `documentacion de referencia`, si existe en el material entregado. Examinarla de forma recursiva antes de redactar; consultar los `.md`, `.txt`, `.docx` y `.pdf` relevantes.
3. Estilo, estructura y maquetación de la memoria actual.
4. Documentación existente en `tfg_informatica_fake_news/docs/` y evidencias del proyecto que permitan comprobar hechos.
5. Normas APA 7 descritas en `12_APA7_ESTILO_Y_BUENAS_PRACTICAS.md`.

En el ZIP revisado para preparar estas instrucciones no aparece una carpeta con el nombre exacto `documentacion de referencia`. Si tampoco existe al ejecutar el trabajo, usar provisionalmente `tfg_informatica_fake_news/docs/` como documentación de apoyo, dejar constancia de la ausencia en `CAMBIOS_REALIZADOS.md` y **no inventar** datos que debieran proceder de esa carpeta.

## Principio de edición conservadora

- Mantener todo el contenido correcto que ya existe.
- Editar por secciones y con cambios localizados; no reconstruir el documento desde cero.
- Reutilizar los estilos de Word, encabezados, pies, portada, logotipo, márgenes, tipografías, colores, tablas, figuras y espaciados existentes.
- No reformular párrafos que no estén afectados por las observaciones de la tutora, salvo correcciones ortográficas inequívocas.
- No introducir afirmaciones nuevas sin respaldo documental.
- No añadir citas o referencias inventadas.
- Si una instrucción admite varias soluciones, elegir la que altere menos el documento y anotarla en el registro de cambios.
- Mantener la estructura general de seis capítulos, salvo los cambios de título, orden o denominación solicitados.

## Límites estrictos

No realizar ninguna de las siguientes acciones:

- modificar código fuente, pruebas, `README`, dependencias o archivos de configuración;
- volver a entrenar modelos o ejecutar nuevos experimentos;
- recalcular o sustituir métricas, matrices de confusión, tablas o resultados;
- modificar datasets o etiquetas;
- publicar cambios en GitHub o Hugging Face;
- afirmar que Telegram se utilizó para entrenar o evaluar los modelos;
- presentar el sistema como detector general de noticias falsas;
- comparar el TFG con un TFG de Computers u otro trabajo estudiantil;
- ocultar la falta de evidencia sobre una fuente, licencia o validación real.

## Datos experimentales que deben conservarse

- Corpus unificado: 50.503 registros.
- Clase 0: 23.470 registros.
- Clase 1 o *fake*: 27.033 registros.
- Modelos comparados: los dos modelos lineales ya documentados.
- Mejor resultado en la partición utilizada: Linear SVC.
- Macro F1 de Linear SVC: 0,9424.
- Pruebas documentadas: 16 superadas y 0 fallidas, solo si esta información sigue respaldada por los artefactos del proyecto.
- Umbrales 0,60 y 0,30: decisiones de diseño conservadoras, no valores aprendidos ni universales.

## Orden de ejecución

Aplicar los archivos en orden numérico. Antes de cada bloque, releer estas instrucciones y `12_APA7_ESTILO_Y_BUENAS_PRACTICAS.md`.

1. Crear copia de trabajo e inventario de estilos.
2. Aplicar `01` a `11`.
3. Realizar la revisión final indicada en `13_CHECKLIST_FINAL_Y_ENTREGA.md`.
4. Actualizar al final los índices, la numeración, las referencias cruzadas y los campos de Word.
5. Exportar a PDF y revisar visualmente todas las páginas.

## Criterio general de aceptación

La revisión será válida si satisface las observaciones de la tutora, conserva el contenido y la identidad visual de la memoria, no altera el proyecto técnico ni sus resultados y deja una trazabilidad clara de lo modificado.
