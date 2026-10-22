# Cambios realizados

> Actualización del repositorio — 22/10/2026: se publican el ejecutor y la configuración del protocolo agrupado, datos y evidencia del run final, modelos comprimidos con restauración verificable, dependencias fijadas y guía de reproducción. La comprobación actual suma 33 pruebas superadas (las 28 anteriores y cinco del paquete de entrega). Los DOCX/PDF no se editan en esta actuación; se conserva además el Word recibido el 21 de octubre como fuente de revisión. Esta comprobación técnica del repositorio no implica aceptar sus revisiones de estilo en Word.

## Entrega reproducible en el repositorio — 22/10/2026

- Se continúa en el repositorio existente `AlvaroOsunaFlores/TFG`, rama `feat/separacion-tfgs`. El alcance del commit corresponde al TFG de Informática y a los ajustes compartidos de README, Git y CI necesarios para su entrega; los cambios locales del TFG de Computadores se conservan aparte.
- El README se actualiza al run principal `robustness-1a94400d502b149f` y enlaza `docs/REPRODUCIBILIDAD.md`. Se distinguen validación interna, transferencia entre fuentes y capacidad no acreditada sobre Telegram. Los resultados de transferencia se explicitan como evidencia de las limitaciones de generalización.
- Se versionan ejecutor, configuraciones, protocolo, pruebas, corpus derivado, particiones, predicciones y manifiestos del run final. Los 14 modelos, la auditoría y dos artefactos históricos adicionales se distribuyen en 17 gzip con restauración y hashes; no se modifica ningún artefacto experimental original. Las ejecuciones exploratorias y los temporales permanecen locales.
- `requirements-reproducible.txt` fija el entorno de comprobación nuevo. NumPy 1.26.4, pandas 2.2.3 y scikit-learn 1.4.2 coinciden con el manifiesto original; las restantes versiones se documentan como entorno actual de comprobación, no como una congelación histórica completa. `pip check` no detecta dependencias incompatibles.
- La configuración `robustness_reproduction.json` conserva los parámetros científicos y separa las nuevas salidas. Los scripts de restauración e integridad funcionan con rutas relativas al proyecto. Git preserva los bytes de los archivos vinculados a SHA-256, incluidos los finales de línea originales.
- Una exportación limpia del índice de Git, sin acceso a los directorios ignorados del proyecto original, restaura los 17 archivos y verifica los hashes de 51 archivos directos. Se contrastan métricas y matrices globales, por fold, fuente y transferencia; 44.408 predicciones OOF por modelo; grupos sin reparto entre folds; y 50.503 estados de auditoría. Se cargan los 14 modelos y coinciden 42 predicciones y puntuaciones de muestra.
- Las 33 pruebas pasan tanto en el proyecto como en la copia limpia: las 28 anteriores y cinco específicas del paquete. La evidencia actual queda en `reports/repository_validation/`; el JUnit de septiembre permanece intacto en su run. No se ejecuta un nuevo entrenamiento completo ni una extracción real.
- La integración continua de GitHub instala las dependencias fijadas, comprueba los modos dry-run, restaura y verifica los artefactos y publica el JUnit. Los archivos originales conservan los hashes documentados. Las revisiones de estilo del Word recibido el 21 de octubre permanecen como actuación editorial separada.

> Estado de entrega vigente (15/10/2026): revisión tipográfica de la integración de Liliana. El PDF tiene **69 páginas A4** y 48 marcadores; el DOCX contiene 30 tablas editables (25 principales y cinco históricas), nueve imágenes, 28 referencias y ninguna revisión ni comentario pendiente. Se conserva el curso **2026-2027**. La verificación actual se documenta en «Corrección final de formato y fidelidad tipográfica — 15/10/2026».

> Las secciones anteriores describen hitos históricos. Cuando una cifra de paginación, estado editorial o método de exportación difiere, prevalece la sección de corrección final situada al término de este registro. Esta actuación no recalculó métricas ni ejecutó pruebas.

## Punto 01 - Portada y titulo

- Se creo una copia de trabajo de la memoria con el nombre `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.docx`; el DOCX original no se ha sobrescrito.
- Se sustituyo el titulo de la portada por: `Diseño de un pipeline experimental reproducible para la clasificación de fake news mediante modelos de aprendizaje automático`.
- Se conservaron el logotipo, los datos institucionales, la alineacion, la negrita, el interlineado y el espaciado del parrafo de titulo existente.
- No se localizaron propiedades de documento, encabezados, pies ni una pagina de titulo independiente que contuvieran el titulo anterior.
- La errata `Ingeniería Informátca` se localizo posteriormente en la tabla del encabezado y se corrigio en el punto 02.
- Se exporto el PDF de revision como `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.pdf` mediante Word.

## Punto 02 - Objetivos y coherencia metodologica

- Se sustituyo el objetivo general por la formulacion metodologica centrada en el corpus unificado, la reproducibilidad y los modelos supervisados TF-IDF.
- Se reemplazaron los siete objetivos especificos y se conservaron su lista automatica, numeracion, sangria y estilo. Telegram queda como el septimo y ultimo objetivo, definido como modulo complementario de adquisicion bajo demanda.
- Se elimino el objetivo de diferenciacion respecto al TFG de Computadores.
- Se ajustaron de forma localizada el resumen, la introduccion, la metodologia de trabajo, los requisitos funcionales, la apertura de la evaluacion y las conclusiones para presentar Telegram como extension independiente, no como objeto validado.
- Se corrigio el encabezado visible `Grado en Ingeniería Informátca` por `Grado en Ingeniería Informática`.
- Se regenero el PDF de revision desde el DOCX actualizado.

## Punto 03 - Resumen y palabras clave

- Se reescribieron conservadoramente los tres parrafos del resumen para presentar, en este orden, el problema metodologico, el proposito, el metodo, el resultado principal, el alcance, el papel complementario de Telegram y la limitacion por fuente y estilo editorial.
- Se conservo el corpus de 50.503 registros y su distribucion por clases; el resultado principal se expresa como macro F1 de `0,9424` para Linear SVC en la particion utilizada.
- Se retiraron del resumen los detalles secundarios de accuracy, precision, recall, tamano del holdout, unigramas, bigramas y politica de umbral, que permanecen documentados en el capitulo de evaluacion.
- Se anadio la linea obligatoria de palabras clave y se conservo el salto de pagina previo a la introduccion.
- No se creo un abstract ni keywords en ingles porque esos elementos no existian en la memoria de entrada.
- Se regenero el PDF de revision desde el DOCX actualizado.

## Punto 04 - Reorganizacion de la introduccion

- Se reescribieron de forma localizada los seis parrafos introductorios anteriores a los objetivos, con una progresion desde la relevancia de la desinformacion y el problema metodologico hasta la reproducibilidad, la solucion propuesta, los limites del estudio y el papel complementario de Telegram.
- Se conservaron las referencias de Lazer, Vosoughi, Shu, Thorne y Vlachos junto a las afirmaciones que respaldan, sin incorporar citas nuevas.
- La contribucion se delimito como metodologica y experimental; los resultados quedan circunscritos al corpus construido a partir de archive2 y LIAR y a la particion documentada.
- Telegram se presenta unicamente al final como modulo independiente de adquisicion bajo demanda. Sus mensajes no etiquetados no participaron en el corpus, el entrenamiento ni la evaluacion, y no se afirma monitorizacion continua, deteccion en tiempo real ni despliegue productivo.
- Se actualizo el parrafo de organizacion de la memoria para describir el contenido vigente de los capitulos y mantener Telegram como modulo complementario.
- Se conservaron los encabezados, los niveles de numeracion, la alineacion justificada, el interlineado 1,5 y los objetivos general y especificos aprobados en el punto 02.
- Se regenero el PDF de revision desde una instancia nueva de Word.

## Punto 05 - Contexto, estado del arte y alcance

- Se reorganizo el capitulo 2 en ocho apartados para presentar primero los fundamentos de desinformacion, clasificacion textual, corpus, TF-IDF, modelos lineales y reproducibilidad, seguidos de los trabajos relacionados, Telegram como dominio futuro y el alcance concreto del TFG.
- Se conservaron y redistribuyeron las explicaciones tecnicas correctas, se eliminaron repeticiones y se mantuvo una extension conservadora de 2.645 palabras incluyendo la Tabla 1.
- Se explicitaron la transformacion binaria de las etiquetas de archive2 y LIAR, el riesgo de sesgo de fuente y la diferencia entre rendimiento interno, fact-checking y generalizacion a otros dominios.
- Telegram se traslado al apartado 2.7 y se delimito como modulo independiente de adquisicion bajo demanda, con mensajes no etiquetados que no participaron en el corpus, el entrenamiento ni la evaluacion.
- La Tabla 1 se conservo como tabla editable y se transformo en una comparacion metodologica de Shu et al. (2017), Wang (2017), Ruchansky et al. (2017) y Ozbay y Alatas (2020).
- Se elimino de la tabla y del capitulo cualquier comparacion con el TFG de Computadores.
- El cierre del capitulo enlaza el alcance metodologico con los requisitos y la arquitectura del capitulo 3.
- Se actualizo el indice automatico y se regenero el PDF de revision desde una instancia nueva de Word.

## Punto 06 - Requisitos y trazabilidad documental

- Se reorganizaron los requisitos funcionales de la Tabla 2 conforme al flujo experimental y se establecio una numeracion continua de `RF-1` a `RF-8`.
- Se incorporo `RF-7` para la reproduccion y auditoria del experimento, y la adquisicion opcional desde Telegram paso a `RF-8`, sin incorporacion ni clasificacion automatica de sus mensajes en la evaluacion actual.
- Se reformularon `RNF-1` a `RNF-6` para identificar de forma expresa reproducibilidad, trazabilidad, robustez ante incoherencias del corpus, mantenibilidad y bajo acoplamiento, separacion de Telegram respecto al experimento y documentacion e interpretabilidad.
- Las tablas 2 y 3 mantienen su formato editable y añaden una tercera columna de trazabilidad que enlaza cada requisito con secciones, artefactos o pruebas existentes y con la evaluacion cuando procede.
- Se verifico la existencia de los scripts, configuraciones, artefactos y pruebas citados, sin ejecutar nuevos experimentos ni declarar un nuevo resultado de pytest.
- No se añadieron requisitos de tiempo real, despliegue, escalabilidad o precision universal.
- Se actualizaron los campos y el indice automatico de Word y se regenero el PDF de revision desde una instancia nueva.

## Punto 07 - Arquitectura funcional y Figura 1

- Se reescribio de forma localizada la seccion 3.4 para distinguir la ruta experimental evaluada y la ruta complementaria de adquisicion desde Telegram.
- La Figura 1 se redibujo como elaboracion propia con dos rutas horizontales independientes y sin flechas que conecten Telegram con el corpus, TF-IDF, los modelos o la evaluacion actuales.
- La ruta evaluada representa archive2 y LIAR, corpus unificado, validacion, preprocesamiento, TF-IDF, modelos y evaluacion y artefactos.
- La ruta complementaria representa Telegram, extraccion, deduplicacion, preprocesamiento y mensajes sin etiquetar destinados a un futuro corpus.
- Se eliminaron de la figura la comparacion con el TFG de Computadores y los parrafos vacios que separaban artificialmente el texto y la figura.
- Se actualizaron el titulo y la nota de la figura y se añadio la explicacion del protocolo de seleccion, anotacion y validacion necesario para una integracion futura.
- La imagen conserva las dimensiones aproximadas de 15,49 x 5,85 cm, la paleta visual y el estilo general de cajas y flechas del documento.

## Punto 08 - Desarrollo y modulo complementario de Telegram

- Se renombro la seccion 4.4 como `Modulo complementario de adquisicion desde Telegram` y se conservo su nivel de encabezado, numeracion y estilo.
- Se establecio de forma explicita que el corpus etiquetado de archive2 y LIAR es la unica fuente del entrenamiento, la comparacion de modelos y la evaluacion; los mensajes de Telegram no participaron en esos experimentos.
- Se documento la adquisicion bajo demanda mediante Telethon, el registro de metadatos, la deduplicacion persistente mediante `canal:message_id`, la normalizacion y la persistencia de la coleccion cruda, los mensajes procesados, el registro y el manifiesto.
- La salida del modulo se delimito como una coleccion sin etiquetar destinada unicamente a apoyar la construccion futura de un corpus del dominio.
- Se indico que cualquier incorporacion experimental posterior requeriria seleccion, protocolo de anotacion, control de calidad, acuerdo entre anotadores y una evaluacion especifica del dominio.
- Se ajustaron de forma localizada los parrafos de implementacion modular de `telegram_extractor.py` y `dataset_manager.py` para mantener el extractor separado del corpus experimental actual.
- Se añadio a 4.9 la descripcion de las pruebas automatizadas de Telegram con `_FakeClient`, identificandolas como simuladas y delimitando que no validan acceso real, credenciales, reintentos reales, deduplicacion persistente, operacion continua, rendimiento ni eficacia en Telegram.
- Se actualizaron los campos y el indice automatico de Word y se regenero el PDF de revision desde una instancia nueva.

## Punto 09 - Evaluacion experimental y analisis de resultados

- Se renombro el capitulo 5 como `Evaluacion experimental y analisis de resultados` y se sincronizaron el indice y el parrafo de organizacion de la memoria.
- Se incorporo una apertura que delimita las metricas al corpus unificado de archive2 y LIAR, a sus 50.503 registros y a la particion holdout estratificada documentada de 12.626 ejemplos. Telegram no intervino en el corpus, el entrenamiento ni la prueba.
- Se mantuvieron sin recalcular las tablas, las figuras, la matriz de confusion, los soportes y las metricas existentes. El resultado principal se expresa como: `Linear SVC obtuvo el mejor resultado de los dos modelos comparados en la particion utilizada, con un macro F1 de 0,9424.`
- Se precisaron los umbrales configurados: `0,60` para la probabilidad de Regresion Logistica y `0,30` para `decision_function` de Linear SVC. Se delimitan como decisiones manuales, no universales ni validadas en otros dominios.
- Se documento la ejecucion de `pytest` con 16 pruebas superadas y 0 fallidas, agrupadas en preprocesamiento, corpus y validacion, adquisicion simulada desde Telegram, entrenamiento, evaluacion y persistencia, y analisis. Las pruebas con `_FakeClient` se describen como control tecnico y no como validacion estadistica ni de generalizacion.
- Se renombro 5.8 como `Interpretacion y limites de validez` y se reescribio para delimitar la validez interna, el sesgo de fuente, la unica particion, la ausencia de evaluacion en Telegram y la necesidad de transferencia de dominio antes de cualquier uso externo.
- El baseline se acepta unicamente como referencia reproducible para el corpus, la particion, el run `baseline-20260411T145313Z-a9ea359a` y el hash documentados. Se ajustaron de forma localizada las conclusiones para mantener esta misma interpretacion.
- Se conservaron los marcadores de los encabezados, las tablas y las figuras; se corrigio la paginacion para mantener juntas las leyendas y sus elementos, repetir la cabecera de la Tabla 14 e impedir la division interna de sus filas.

## Punto 10 - Conclusiones y trabajo futuro

- Se reescribio el capitulo 6 en cinco parrafos academicos para eliminar conclusiones repetidas, resúmenes redundantes y parrafos vacios innecesarios.
- La apertura reproduce la formulacion obligatoria sobre el cumplimiento del objetivo general y la metodologia experimental reproducible.
- Las contribuciones responden de forma verificable a los siete objetivos especificos: corpus, preprocesamiento, validacion, modelos TF-IDF, evaluacion, persistencia y adquisicion complementaria desde Telegram.
- El resultado principal conserva la formulacion exacta de Linear SVC y macro F1 `0,9424`, seguido de su limitacion por fuente, formato y estilo editorial.
- Se sintetizaron las limitaciones relativas a datasets externos, sesgo de procedencia, binarizacion, una unica particion, ausencia de corpus anotado de Telegram y falta de transferencia de dominio.
- El trabajo futuro se limita a propuestas no ejecutadas: corpus Telegram anotado, protocolo de calidad, transferencia, particiones por fuente o periodo, analisis de errores, calibracion, explicabilidad y modelos avanzados tras una evaluacion adecuada del dominio.
- Se conservo el titulo del capitulo, los estilos Normal/Heading 1 y la transicion a Bibliografia mediante un salto de pagina explicito.

## Punto 11 - Correcciones formales, bibliografía, índices y referencias cruzadas

- Se corrigieron erratas inequívocas de tildes en la Tabla 7 y se ajustaron de forma localizada varias formulaciones imperativas para mantener la voz académica e impersonal.
- Se verificó que `Ingeniería Informátca` no aparece en ninguna historia Word ni en el PDF; el encabezado correcto se conservó sin cambios adicionales.
- Se desarrollaron las siglas TF-IDF, HTML, URL, BERT, Linear SVC, CNN, API, JSON, CSV, SHA-256 y UTC en su primera explicación útil, manteniendo intacta la formulación obligatoria del resultado de Linear SVC.
- Se incorporó en 4.1 que el corpus es casi enteramente inglés: la metadata confirma la detección `en` en 50.421 de los 50.503 registros. Las detecciones restantes se delimitan como minoritarias y potencialmente ruidosas, no como validación multilingüe.
- La documentación disponible identifica `archive2` y los ficheros `Fake.csv` y `True.csv`, pero no permite confirmar su página de procedencia ni su licencia. No se atribuyó una licencia ni se añadió una referencia bibliográfica no verificable.
- Se consolidó la bibliografía en una única lista alfabética de nueve obras citadas. Se eliminaron cinco referencias duplicadas y doce entradas no citadas, conservando las versiones más completas con DOI o URL ya verificables cuando existían.
- Las referencias finales mantienen sangría francesa de 1,27 cm, Times New Roman 12 pt, interlineado 1,5, 6 pt posteriores y las cursivas correspondientes conforme a APA 7.
- Se actualizaron todos los campos y el índice general de Word. No existen índices independientes de figuras o tablas; se comprobó manualmente la secuencia Figura 1–8, Tabla 1–14 y Tabla A.1, así como sus referencias en el texto.
- Se corrigió la paginación para mantener juntos el número, título y cabecera de la Tabla 7, y para impedir que una referencia bibliográfica se divida entre páginas.

## Punto 12 - Auditoría APA 7 y estilo académico

- Se realizó una auditoría formal adicional y conservadora sobre las citas, siglas, notas, títulos, referencias cruzadas y bibliografía de la memoria de revisión, sin modificar el contenido técnico, los datos, las métricas, las tablas ni las figuras.
- Se confirmó la correspondencia bidireccional entre las nueve obras citadas y las nueve referencias finales, sin referencias duplicadas ni entradas bibliográficas huérfanas.
- Se completó la referencia de Devlin et al. con la inicial `M.-W.`, los tres editores, el título completo de las actas y su DOI verificable.
- Se incorporaron los DOI verificables de Gravanis et al., Ozbay y Alatas y Ruchansky et al.; en esta última entrada se normalizó el editor como `Association for Computing Machinery`.
- Se mantuvo la URL de ACL para Thorne y Vlachos al no existir DOI en la ficha oficial consultada, y se preservaron la lista alfabética, la sangría francesa de 1,27 cm, Times New Roman de 12 pt, el interlineado 1,5, los 6 pt posteriores y las cursivas pertinentes.
- No se añadieron referencias, licencias ni procedencias no verificadas; en particular, se conserva la delimitación documental de `archive2`.

## Ampliación documental y correcciones previas (registro histórico, supersedido por el cierre experimental)

- Se amplió la memoria de revisión a partir de evidencia ya presente en el repositorio, sin ejecutar entrenamientos ni incorporar métricas, modelos, datos o resultados nuevos.
- Los capítulos 3, 4 y 5 incorporan detalle adicional sobre fases metodológicas, contratos entre datos y modelo, validación estructural, preprocesamiento determinista, configuración TF-IDF, umbrales, persistencia de artefactos, pruebas automatizadas, interpretación de errores y límites de validez.
- Se añadieron los apéndices B a F: esquema canónico del corpus; contrato de validación y preprocesamiento; configuración, manifiesto, hash y reproducción auditable; mapa de las 16 pruebas y sus límites; y catálogo ampliado de términos influyentes.
- Los nuevos anexos usan tablas Word editables con numeración propia: Tabla B.1 a B.3, Tabla C.1 a C.3, Tabla D.1 a D.3, Tabla E.1 a E.2 y Tabla F.1 a F.4. Las Figuras 1 a 8 y los datos de las Tablas 1 a 14, incluida la Tabla A.1, se conservaron sin cambios.
- Toda la documentación nueva se limita al run `baseline-20260411T145313Z-a9ea359a`, a su hash de corpus documentado y al experimento archive2+LIAR. Telegram se mantiene como módulo complementario independiente, sin participación en corpus, entrenamiento, evaluación ni resultados.
- Se actualizaron los campos y el índice general mediante una instancia nueva de Word y se realizó la exportación final solo tras validar una copia temporal.
- Corrección final de incidencias: se sustituyó en 3.8 la referencia obsoleta a un título centrado en Telegram; la Tabla 1 quedó completa en una página con cabecera repetible y filas indivisibles; la Tabla 8 se simplificó a tres columnas sin pérdida de datos; y se eliminaron cinco párrafos vacíos con estilo Heading 2.
- Las Tablas B.1 a F.4 incorporan referencia previa, nota situada después de la tabla y fuente Times New Roman de 10 pt. Se ajustaron únicamente sus márgenes e interlineado internos para conservar una extensión final de 65 páginas sin reducir la fuente ni eliminar contenido técnico.

## Validaciones históricas de versiones anteriores

Las declaraciones siguientes conservan el historial de las actuaciones anteriores; no constituyen por sí solas evidencia de cumplimiento de la versión actual. Sus referencias a 45, 46, 47 o 64 páginas y a páginas interiores no deben utilizarse como paginación de la revisión de 65 páginas. En particular, el resultado histórico de pytest no se ha podido confirmar mediante un informe de ejecución independiente en esta auditoría.

- El nuevo titulo aparece una sola vez en el DOCX y una sola vez en el PDF de revision.
- El titulo anterior no aparece en ninguna historia Word ni en el PDF de revision.
- La portada se reviso visualmente tras la exportacion: el titulo queda centrado en dos lineas y no presenta cortes, solapamientos ni desbordamientos.
- El DOCX original conserva su huella SHA-256: `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399`.
- El objetivo general y los siete objetivos especificos se verificaron en el DOCX y en el PDF, en el orden solicitado y con Telegram como ultimo punto.
- La lista conserva su formato automatico existente y el encabezado corregido se verifico en el DOCX y en el PDF.
- Se revisaron visualmente las paginas del PDF que contienen los objetivos; no presentan texto cortado, desbordamientos ni solapamientos.
- El resumen final contiene 287 palabras, mantiene tres parrafos justificados y expresa el macro F1 como `0,9424`.
- Las palabras clave se verificaron en el DOCX y en el PDF con la etiqueta en negrita, el contenido exacto y alineacion izquierda.
- Se revisaron visualmente la pagina del resumen y el comienzo de la introduccion; el contenido no se desborda y el salto de pagina permanece intacto.
- La introduccion revisada contiene 553 palabras frente a las 559 anteriores; mantiene los seis parrafos, el estilo Normal, la alineacion justificada y el interlineado 1,5.
- Se revisaron visualmente las paginas 5 a 7 del PDF: la introduccion, la motivacion, los objetivos y la estructura no presentan texto cortado, desbordamientos ni solapamientos.
- El indice incluye los apartados 2.1 a 2.8 en el orden previsto y ya no contiene las denominaciones anteriores del capitulo 2.
- Se verifico que Telegram aparece despues de los trabajos relacionados, que sus mensajes no se atribuyen al corpus evaluado y que no quedan comparaciones con otros TFG en el documento de revision.
- La Tabla 1 conserva cuatro columnas y cuatro trabajos académicos. La afirmación anterior de que ya permanecía completa en una página no se considera una validación histórica fiable; la comprobación actual la sitúa completa en la página física 14.
- Se revisaron visualmente las paginas 7 a 15 del PDF; el capitulo 2 y su transicion al capitulo 3 no presentan texto cortado, tablas partidas, solapamientos ni paginas vacias accidentales.
- La Tabla 2 contiene exclusivamente `RF-1` a `RF-8` y la Tabla 3 contiene exclusivamente `RNF-1` a `RNF-6`, con tres columnas, fuente de 10 pt y anchos aproximados de 1,7 / 7,3 / 7,0 cm.
- Se verificaron el encabezado repetible y la prohibicion de dividir filas entre paginas en ambas tablas; cada tabla, su titulo y su nota permanecen completos en una sola pagina.
- Se revisaron visualmente las paginas 15 a 18 del PDF: las tablas de requisitos y la transicion a 3.4 no presentan texto cortado, desbordamientos ni solapamientos.
- El objetivo general y los siete objetivos especificos del punto 02 permanecen intactos, con Telegram como septimo y ultimo objetivo especifico.
- Tras el punto 07, el PDF de revision contenia 45 paginas y el indice actualizado situaba 3.2 en la pagina numerada 11 y 3.3 en la pagina numerada 13.
- La Figura 1 mantiene unas dimensiones de 15,49 x 5,85 cm y presenta en la pagina numerada 14 las dos rutas completas, legibles y sin conexiones ambiguas entre ellas.
- El numero, el titulo, la imagen y la nota de la Figura 1 permanecen juntos; `Nota.` no se divide y la figura se cita previamente en el texto de 3.4.
- Se verifico en el DOCX y en el PDF que no queda la comparacion con el TFG de Computadores ni se atribuye a Telegram participacion en el corpus, TF-IDF, los modelos o la evaluacion actuales.
- Se revisaron visualmente las 45 paginas del PDF y con mayor detalle las paginas fisicas 17 a 19; no se detectaron recortes, desbordamientos, solapamientos ni paginas vacias accidentales.
- El titulo actualizado de 4.4 aparece en el indice y en el cuerpo del DOCX/PDF; la denominacion anterior ya no aparece.
- Se verifico que 4.4 atribuye los resultados exclusivamente al corpus de archive2 y LIAR, que la salida de Telegram permanece sin etiquetar y que no se afirma monitorizacion continua, despliegue productivo ni validacion con canales reales.
- Las pruebas de Telegram se identifican expresamente como automatizadas y simuladas mediante `_FakeClient`; sus limites se comprobaron frente al codigo y las pruebas existentes sin ejecutar extracciones ni nuevos experimentos.
- Se conservaron el marcador del encabezado 4.4, los estilos Normal/Heading 2, la justificacion, el interlineado 1,5, el espaciado posterior y el salto de pagina anterior al capitulo 5.
- El PDF posterior al punto 08 contiene 47 paginas. Se revisaron visualmente todas ellas y con mayor detalle las paginas fisicas 26 a 34; no presentan texto cortado, solapamientos, encabezados aislados ni paginas vacias accidentales.
- El indice actualizado situa 4.4 en la pagina numerada 22, 4.8 en la 26, 4.9 en la 28 y el capitulo 5 en la 30.
- El DOCX original conserva su huella SHA-256 `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399` y el PDF original conserva `a2575833d69b947b8bc27cb63210d79f8e0aac5bf094d28e362e875758749180`.
- El indice actualizado contiene `5. Evaluacion experimental y analisis de resultados` en la pagina numerada 30 y `5.8 Interpretacion y limites de validez` en la pagina 35; no conserva las denominaciones anteriores.
- Las cinco tablas del capitulo 5, las nueve imagenes insertadas y sus dimensiones se compararon antes y despues de la edicion y permanecen sin cambios de contenido.
- La formulacion exacta del resultado principal aparece en el resumen, el capitulo 5 y las conclusiones; Telegram no recibe metricas ni se atribuye al corpus, al entrenamiento o a la evaluacion.
- El registro anterior declaró 16 pruebas superadas y 0 fallidas con `pytest -q`. No se conserva un informe de ejecución independiente que permita verificar actualmente esa declaración. No se ha ejecutado pytest en el cierre; algunas pruebas entrenan modelos sintéticos, por lo que tampoco se mantiene la afirmación histórica de que ejecutar toda la suite no implicaba entrenamiento alguno.
- El PDF de revision posterior al punto 09 contiene 47 paginas. Se revisaron visualmente todas las paginas mediante hojas de contacto y, en detalle, el indice, el resumen, las paginas 30 a 37 de la memoria, las Figuras 6 a 8, las Tablas 10 a 14 y la transicion al capitulo 6; no se detectaron recortes, solapamientos, filas partidas ni paginas vacias accidentales.
- El capitulo 6 contiene exactamente cinco parrafos de cuerpo entre su encabezado y Bibliografia; mantiene Times New Roman 12 pt, alineacion justificada, interlineado 1,5 y 6 pt posteriores.
- La formulacion del resultado principal coincide exactamente entre resumen, evaluacion y conclusiones. No aparecen afirmaciones de validacion en Telegram, generalizacion universal ni despliegue productivo.
- Las 15 tablas y las 9 imagenes insertadas conservan su contenido y dimensiones tras la reescritura del capitulo final.
- Se actualizo el indice automatico y se regenero el PDF de revision desde una instancia nueva de Word; se revisaron visualmente las conclusiones, la bibliografia y el documento completo.
- El PDF de revision posterior al punto 10 contiene 46 paginas: las conclusiones ocupan una pagina y Bibliografia comienza en la siguiente, sin paginas vacias accidentales.
- Tras el punto 11, el PDF de revision contiene 45 paginas. Se revisaron visualmente el índice, la Tabla 6, la Tabla 7, la bibliografía, el glosario, el apéndice y las páginas afectadas; no presentan recortes, solapamientos, notas partidas ni páginas vacías accidentales.
- La bibliografía final contiene exclusivamente las nueve referencias citadas en el cuerpo y la Tabla 1. No quedan referencias duplicadas ni entradas bibliográficas sin cita.
- El DOCX original conserva su huella SHA-256 `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399` y el PDF original conserva `a2575833d69b947b8bc27cb63210d79f8e0aac5bf094d28e362e875758749180`.
- La auditoría adicional del punto 12 confirmó las nueve correspondencias cita–referencia y los DOI añadidos de Devlin, Gravanis, Ozbay y Ruchansky; la URL de ACL de Thorne y Vlachos se conserva como enlace sin DOI.
- Se actualizaron los campos del cuerpo y el índice general en una instancia nueva de Word. El PDF temporal de Word se revisó íntegramente: contiene 45 páginas, no tiene páginas vacías, y no presenta recortes, solapamientos ni divisiones internas de las referencias.
- Se revisaron específicamente portada, índice, resumen, bibliografía, glosario y apéndice. Se mantiene la frase obligatoria de Linear SVC y Telegram no se atribuye al corpus, entrenamiento ni evaluación experimental.
- Una versión histórica de la ampliación contenía 64 páginas. Esta cifra y su validación visual no describen la revisión actual de 65 páginas; la auditoría actual sí ha localizado la leyenda de la Figura 4 separada de su imagen.
- El índice general incluye los apéndices B a F en las páginas impresas 47 a 55. Las páginas físicas 51 a 64 se revisaron en detalle, incluidas las nuevas tablas, la transición desde el Apéndice A y el cierre del Apéndice F.
- La validación textual final confirmó una sola aparición del título de portada, ausencia del título anterior, tres apariciones de la formulación obligatoria de Linear SVC, presencia de las Figuras 1 a 8 y de las Tablas 1 a 14, y presencia de las quince tablas nuevas B.1 a F.4.
- La validación final confirmó que no se incorpora el resultado de corpus completo, no hay comparaciones con el TFG de Computadores y no se atribuye a Telegram participación en el corpus, el entrenamiento o la evaluación. Las menciones a monitorización continua o detección en tiempo real se conservan únicamente para negar que el módulo posea esas capacidades.
- El DOCX original conserva su huella SHA-256 `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399` y el PDF original conserva `a2575833d69b947b8bc27cb63210d79f8e0aac5bf094d28e362e875758749180`.

## Fuentes consultadas

- `INSTRUCCIONES_MEMORIA_TFG/00_INSTRUCCIONES_MAESTRAS_CODEX.md`
- `INSTRUCCIONES_MEMORIA_TFG/01_PORTADA_Y_TITULO.md`
- `INSTRUCCIONES_MEMORIA_TFG/02_OBJETIVOS.md`
- `INSTRUCCIONES_MEMORIA_TFG/03_RESUMEN_PALABRAS_CLAVE_Y_ABSTRACT.md`
- `INSTRUCCIONES_MEMORIA_TFG/04_INTRODUCCION.md`
- `INSTRUCCIONES_MEMORIA_TFG/05_CONTEXTO_ESTADO_DEL_ARTE_Y_ALCANCE.md`
- `INSTRUCCIONES_MEMORIA_TFG/06_REQUISITOS.md`
- `INSTRUCCIONES_MEMORIA_TFG/07_ARQUITECTURA_Y_FIGURA_1.md`
- `INSTRUCCIONES_MEMORIA_TFG/08_DESARROLLO_Y_MODULO_TELEGRAM.md`
- `INSTRUCCIONES_MEMORIA_TFG/09_EVALUACION_Y_RESULTADOS.md`
- `INSTRUCCIONES_MEMORIA_TFG/10_CONCLUSIONES_Y_TRABAJO_FUTURO.md`
- `INSTRUCCIONES_MEMORIA_TFG/11_CORRECCIONES_FORMALES_BIBLIOGRAFIA_E_INDICES.md`
- `INSTRUCCIONES_MEMORIA_TFG/12_APA7_ESTILO_Y_BUENAS_PRACTICAS.md`
- `INSTRUCCIONES_MEMORIA_TFG/INSTRUCCIONES_MEMORIA_TFG/13_CHECKLIST_FINAL_Y_ENTREGA.md`, utilizada para la auditoría individual de cierre. Los ficheros de instrucciones anteriores también se encuentran dentro de esta carpeta anidada.
- Publicaciones primarias de Shu et al. (2017), Wang (2017), Ruchansky et al. (2017) y Ozbay y Alatas (2020), enlazadas en la bibliografia existente.
- Fichas bibliográficas verificadas de Devlin et al. (2019) en ACL Anthology, de Gravanis et al. (2019), de Ozbay y Alatas (2020) en ScienceDirect y de Ruchansky et al. (2017) en DBLP.
- `data/labeled/fake_news_unified.metadata.json`, `data/labeled/README.md`, `README.md` y `docs/MEMORIA_TFG_ETSII_APA7.md` para verificar la composición lingüística del corpus y la información documental disponible sobre `archive2`.
- `scripts/build_real_dataset.py`, `scripts/validate_dataset.py`, `preprocessing.py`, `training_config.json`, `reports/training_runs/baseline-20260411T145313Z-a9ea359a/training_manifest.json`, `comparison.json`, `classification_report.json`, `confusion_matrix.json`, `holdout_predictions.csv`, `prediction_examples.json` y `linear_model_terms.json` del run de referencia.
- `tests/`, `telegram_extractor.py`, `pipeline.py`, `dataset_manager.py` y los artefactos persistidos del baseline para documentar la cobertura de las 16 pruebas y sus límites técnicos, sin realizar nuevas extracciones, entrenamientos ni evaluaciones.
- Memoria y PDF originales incluidos en `docs/`.

## Pendientes y alcance

- La carpeta con el nombre literal `documentacion de referencia` no está dentro del proyecto; sí existe `documentacion_referencia` en la raíz de trabajo. La afirmación anterior sobre ausencia de documentación de referencia queda rectificada.
- La licencia y la página de procedencia de `archive2` no se han podido confirmar con la documentación disponible; esta cuestión queda registrada sin atribuir una licencia no verificada.
- Los puntos 01–13 están aplicados y las incidencias documentales y de maquetación identificadas están resueltas. Persisten únicamente las limitaciones de evidencia que se explicitan en el checklist final.

## Punto 13 — Checklist final de la versión anterior (histórico, supersedido por el cierre experimental)

La versión final tiene **64 páginas físicas**, curso **2026-2027** y **52 marcadores de navegación** generados por Word a partir de los encabezados. Se revisaron todas las páginas individualmente a tamaño legible. Tras el último ajuste se compararon las imágenes de todas las páginas y se volvieron a inspeccionar las nueve que cambiaron: 3, 34–37, 44–46 y 53. Las páginas citadas a continuación son físicas, contando la portada; las del cuerpo llevan numeración impresa cuatro unidades menor.

Estados: **C**, comprobado; **L**, limitación real registrada; **NA**, no aplicable. Las limitaciones no se presentan como verificaciones satisfactorias de evidencia inexistente.

### Alcance y seguridad

- [x] **C — Copia de trabajo.** Se conservaron copias previas; la preparación, actualización de campos y exportación se realizaron sobre un DOCX temporal antes de publicar.
- [x] **C — Originales intactos.** SHA-256 DOCX: `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399`. SHA-256 PDF: `a2575833d69b947b8bc27cb63210d79f8e0aac5bf094d28e362e875758749180`.
- [x] **C — Sin cambios técnicos ni remotos.** Los 83 archivos protegidos de código, pruebas, configuración, datos y artefactos conservan sus hashes respecto al inicio de esta auditoría. No se realizaron escrituras en GitHub ni Hugging Face.
- [x] **C — Sin experimentos nuevos.** No se ejecutaron pytest, entrenamientos, extracciones ni cálculos de métricas; se inspeccionaron las evidencias existentes.
- [x] **L — Carpeta de referencia.** El directorio disponible se llama `documentacion_referencia` y se encuentra en la raíz `TFGs`; la ausencia se refería solo al nombre literal y a la ubicación prevista dentro del proyecto.
- [x] **C — Contenido correcto conservado.** Comparación antes/después: texto de las 30 tablas idéntico, nueve imágenes insertadas con bytes preservados, resumen, objetivos, cinco párrafos de conclusiones y nueve referencias bibliográficas sin cambios de contenido.

### Contenido solicitado por la tutora

- [x] **C — Nuevo título en los lugares pertinentes.** Portada, p. 1; una aparición de «Diseño de un pipeline experimental reproducible para la clasificación de fake news mediante modelos de aprendizaje automático». Sin título anterior en las historias Word ni en el PDF.
- [x] **C — Objetivo general metodológico.** 1.2, p. 6: metodología reproducible, corpus unificado y comparación supervisada TF-IDF.
- [x] **C — Siete objetivos en orden.** 1.2, pp. 6–7: corpus, preprocesamiento, validación, modelos, evaluación, persistencia y Telegram; lista automática existente conservada.
- [x] **C/NA — Resumen y abstract.** Resumen p. 4, con alcance experimental y Telegram complementario; **abstract inglés NA**, porque no existía y se acordó no crearlo.
- [x] **C — Palabras clave.** P. 4: «Palabras clave: fake news; clasificación textual; aprendizaje automático; TF-IDF; reproducibilidad; procesamiento del lenguaje natural», con etiqueta en negrita. Keywords inglesas: NA.
- [x] **C — Introducción metodológica antes de Telegram.** 1 y 1.1, pp. 5–6: problema, método, límites y extensión complementaria.
- [x] **C — Reproducibilidad y sesgo antes de Telegram en el contexto.** 2.5, pp. 11–12; trabajos relacionados en 2.6 y Telegram en 2.7, pp. 14–15; secuencia 2.1–2.8 conservada.
- [x] **C — Sin comparación con otros TFG.** Cuerpo, tablas y Figura 1; Tabla 1 contiene exclusivamente cuatro trabajos académicos. 3.8, p. 23, ya no presenta Telegram como título central.
- [x] **C — RF-1–RF-8 y RF-8 opcional.** Tabla 2, pp. 17–18; Tabla 3, pp. 18–19, conserva RNF-1–RNF-6 y la separación de Telegram en RNF-5. Tercera columna de trazabilidad conservada.
- [x] **C — Figura 1 independiente.** P. 19: dos rutas sin flechas de Telegram hacia corpus, TF-IDF, modelos o evaluación.
- [x] **C — Título 4.4.** «Módulo complementario de adquisición desde Telegram», p. 30 y p. 2 del índice.
- [x] **C — Telegram simulado en las pruebas.** 4.9, p. 37; 5.6, pp. 43–44; Apéndice E, pp. 57–58; coherente con `_FakeClient` en el código de pruebas.
- [x] **C — Título del capítulo 5.** «Evaluación experimental y análisis de resultados», p. 38 e índice p. 3.
- [x] **C — Título 5.8.** «Interpretación y límites de validez», p. 45 e índice p. 3.
- [x] **C — Conclusiones.** P. 47: apertura indicada, cinco párrafos y una página, sin alterar sus contribuciones, limitaciones o trabajo futuro; bibliografía desde p. 48.

### Coherencia experimental

- [x] **C — 50.503 registros.** Resumen, Tabla 6 p. 27, apertura del capítulo 5 p. 38; `data/labeled/fake_news_unified.metadata.json`.
- [x] **C — Clase 0: 23.470.** Mismos apartados y metadata; `verificado_o_neutro`.
- [x] **C — Clase 1: 27.033.** Mismos apartados y metadata; `fake_news`.
- [x] **C — Mejor modelo limitado a los dos candidatos y a la partición.** Frase idéntica en pp. 4, 38 y 47: «Linear SVC obtuvo el mejor resultado de los dos modelos comparados en la partición utilizada, con un macro F1 de 0,9424.»
- [x] **C — Macro F1 0,9424.** Tabla 10 p. 39 y `comparison.json` del baseline: `0.9424466609528606` antes del redondeo. No se recalculó.
- [x] **C — Umbrales de diseño.** 4.5 y 5.3, pp. 32 y 41: `0,60` para probabilidad logística y `0,30` para `decision_function`; manuales, no universales ni aprendidos. No hay abstención inventada.
- [x] **L — Resultado histórico de pruebas.** Se localizaron 16 funciones, no un informe independiente de pytest/JUnit que confirme los 16 éxitos y 0 fallos declarados anteriormente. 5.6 p. 43 y Apéndice E pp. 57–58 califican expresamente el dato como histórico y no verificable de nuevo con ese informe ausente. No se declara una nueva ejecución ni se confunde inventario estático con éxito de ejecución.
- [x] **C — Telegram excluido del experimento.** Resumen, 3.4, 4.4, 4.9, 5.1, 5.8, conclusiones y apéndices E–F: material sin etiquetar para un futuro corpus, no fuente de métricas actuales.
- [x] **C — Baseline limitado.** 5.9 pp. 45–46 y apéndices A y D: run `baseline-20260411T145313Z-a9ea359a`, holdout de 12.626 ejemplos y hash `cfaf1b39c0260008e9328950649c9b83de2a9eadb478f631fb9cbc68d1b0a6b1`, no detector general.

### APA 7 y bibliografía

- [x] **C — Todas las citas tienen referencia.** Cotejo del cuerpo y Tabla 1 con Bibliografía pp. 48–49: Devlin, Gravanis, Lazer, Ozbay y Alatas, Ruchansky, Shu, Thorne y Vlachos, Vosoughi y Wang.
- [x] **C — Todas las referencias están citadas.** Nueve obras presentes en introducción, contexto o Tabla 1; sin entradas huérfanas.
- [x] **C — Una única bibliografía.** Nueve entradas en pp. 48–49; sin bibliografías añadidas en apéndices.
- [x] **C — Sin duplicados.** Nueve combinaciones autor/año/título distintas; conservadas las entradas completas aprobadas.
- [x] **C/L — Metadatos verificables, sin invención.** Se conservan los metadatos verificados en el punto 12; se recontrastaron fichas accesibles de ACL y las fuentes de Gravanis y Ozbay/Alatas durante la auditoría. Algunos resolutores DOI no respondieron; no se certifica disponibilidad permanente de todos los enlaces. Se corrigieron únicamente dos citas parentéticas de Thorne y Vlachos a `&`, pp. 8 y 13. Bibliografía sin alteración de contenido.
- [x] **C — DOI en formato URL.** Ocho entradas con `https://doi.org/...`; Thorne y Vlachos mantiene URL de ACL sin DOI inventado.
- [x] **C — Orden y sangría.** Lista alfabética, sangría francesa 1,27 cm, Times New Roman 12 pt, interlineado 1,5 y 6 pt posteriores.
- [x] **C — Número, título, mención y nota.** Secuencias Figura 1–8, Tabla 1–14, A.1 y B.1–F.4 presentes; notas cuando procede. Figura 4 completa en p. 32, con nota en párrafo separado. Inventario de apéndices abajo.

### Formato y estilo

- [x] **C — Formato institucional.** A4, márgenes aproximados de 25 mm, cuerpo Times New Roman 12 pt, justificado e interlineado 1,5; tablas de 10 pt conforme a las excepciones aprobadas. Anexos con interlineado natural, no el fijo de 9,5 pt anterior.
- [x] **C — Estilos de encabezados.** Heading 1/Heading 2 reutilizados; sin los encabezados vacíos eliminados en la revisión anterior.
- [x] **C — Portada e identidad visual.** Logotipo, título, paleta, encabezados y pies preservados. Única corrección nueva en la portada: **Curso Académico 2026-2027**, solicitada expresamente; comprobada en DOCX y p. 1 del PDF.
- [x] **C — Errata institucional ausente.** No aparece `Ingeniería Informátca`; se conserva «Grado en Ingeniería Informática».
- [x] **C — Sin instrucciones editoriales residuales identificadas.** Revisión del cuerpo, tablas y notas; los infinitivos del protocolo son denominaciones de etapas.
- [x] **C — Sin páginas vacías accidentales.** Inspección individual de las 64 páginas; espacios libres asociados a transiciones y paginación, no páginas en blanco.
- [x] **C — Legibilidad y paginación.** No se detectaron recortes, solapamientos ni títulos de figuras separados de sus imágenes. Tabla 1 completa en p. 14; tablas 9 y 14 completas en pp. 34 y 44. Las tablas que continúan repiten cabecera y mantienen filas indivisibles.
- [x] **C — `Nota.` no partida.** Comprobación de todas las notas, incluidas las quince tablas nuevas. Notas de anexos debajo de la tabla, con solo la etiqueta en cursiva.

### Índices y referencias cruzadas

- [x] **C — Campos actualizados en Word.** Se actualizaron las historias Word y el índice en una instancia nueva, se repaginó y se guardó el DOCX antes de exportar.
- [x] **C — Índice coherente.** Pp. 2–3 contrastadas con cuerpo y 52 marcadores: capítulo 5 impresa 34/física 38; 5.9 impresa 41/física 45; conclusiones 43/47; bibliografía 44/48; apéndices A–F en físicas 50, 51, 53, 55, 57 y 59.
- [x] **NA — Índices independientes de tablas/figuras.** No existían y se mantiene la decisión de no crearlos.
- [x] **C — Numeración y referencias sin huérfanos.** Ocho figuras, catorce tablas principales, A.1 y quince tablas nuevas, con menciones previas. Los 52 marcadores apuntan a los encabezados correspondientes.
- [x] **C — Organización actualizada.** 1.3 p. 7: referencia breve explícita a los apéndices A–F y su función, además de los seis capítulos.

### Revisión visual y entregables

- [x] **C — Exportación final mediante Word.** Se resolvió el bloqueo de automatización al cerrar los auxiliares pendientes y ejecutar Word mediante VBScript/COM. `ExportAsFixedFormat` generó el PDF final, incluyendo marcadores de encabezados. La prueba anterior de LibreOffice fue descartada; no es el PDF entregado.
- [x] **C — Todas las páginas revisadas visualmente.** 1–64 a tamaño legible, no solo hojas de contacto. La última iteración se contrastó mediante comparación de imágenes de todas las páginas y reinspección individual de las nueve modificadas.
- [x] **C — Incidencias corregidas y verificadas.** Figura 4 unida a su leyenda y nota; altura de línea legible en anexos; cabeceras repetibles y filas indivisibles; últimas filas de tablas 9 y 14 mantenidas en su página sin reducir fuente ni eliminar contenido.
- [x] **C — Registro actualizado.** Se distinguen las validaciones históricas de 45–65 páginas de la entrega actual de 64; constan fuentes, decisiones conservadoras y limitaciones.
- [x] **C — Tres entregables de revisión publicados tras validar:**
  - [x] `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.docx`.
  - [x] `TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.pdf`.
  - [x] `CAMBIOS_REALIZADOS.md`.

### Evidencias de las quince tablas nuevas

Todas son editables, conservan sus datos y fuente de 10 pt, y tienen mención explícita en el párrafo anterior, número, título y nota posterior. F.4 continúa con cabecera repetida; ninguna fila se divide internamente.

| Tabla | Página física final | Evidencia y alcance |
| --- | --- | --- |
| B.1 | 51 | Esquema canónico; metadata, README de datos y constructor. |
| B.2 | 51 | Inclusión/exclusión y binarización; constructor y metadata. |
| B.3 | 52 | Fases y contratos de salida; módulos existentes. |
| C.1 | 53 | Validación estructural; `scripts/validate_dataset.py`. |
| C.2 | 53 | Transformación y banderas; `preprocessing.py` y metadata. |
| C.3 | 54 | Límites de controles estructurales frente a validez semántica. |
| D.1 | 55 | Configuración y manifiesto del baseline; parámetros sin cambios. |
| D.2 | 55 | Artefactos persistidos y rutas del manifiesto. |
| D.3 | 56 | Run, hash y protocolo de reproducción, no ejecución nueva. |
| E.1 | 57 | Inventario 4+3+3+2+1+3, no confirmación nueva de éxitos. |
| E.2 | 58 | Componentes y límites de los tests, incluido `_FakeClient`. |
| F.1 | 59 | Pesos existentes en `linear_model_terms.json` del baseline. |
| F.2 | 60 | Interpretación no causal de los pesos. |
| F.3 | 61 | Auditoría vinculada a artefactos, no transferencia demostrada. |
| F.4 | 62–63 | Artefactos de análisis, cabecera repetida y nota final en p. 63. |

Tablas principales: 1 en p. 14; 2 y 3 en pp. 17–19; 4 en p. 20; 5 en pp. 26–27; 6 en p. 27; 7 en p. 30; 8 en pp. 33–34, con sus tres columnas; 9 en p. 34; 10–14 en pp. 39, 40, 41, 42 y 44; A.1 en p. 50.

### Limitaciones que permanecen explícitas

- Existe `documentacion_referencia` en la raíz de trabajo. La procedencia de la redistribución de archive2 se documentó después mediante el identificador de Kaggle y la relación con ISOT; su licencia y la procedencia individual de cada registro siguen sin confirmarse.
- Se conserva el resultado de pytest como declaración histórica, no como resultado actualmente verificado. Inventario estático: `test_preprocessing.py` (4), `test_build_real_dataset.py` (1), `test_seed_dataset.py` (2), `test_telegram_extractor.py` (3), `test_train_baseline.py` (1), `test_training_config.py` (1), `test_evaluate_baseline.py` (1) y `test_analysis_utils.py` (3). No hay informe independiente disponible ni nueva ejecución.
- Los 50.421 registros detectados como `en` no acreditan evaluación multilingüe. Telegram continúa excluido de corpus, entrenamiento y evaluación. Las métricas pertenecen únicamente al baseline documentado.

**Cierre:** puntos 01–13 aplicados dentro del alcance documental, con las limitaciones anteriores registradas. El PDF final procede de Word y coincide con el DOCX guardado antes de exportarlo. Los originales no se han sobrescrito y no se han modificado archivos técnicos del proyecto.

## Cierre experimental y revisión de la tutora — 24/09/2026

Esta sección describe la versión preparada para entrega y reemplaza las declaraciones anteriores de 64–65 páginas, nueve referencias, 16 pruebas y evaluación por holdout como evidencia principal. Los archivos publicados se mantuvieron intactos durante el trabajo; esta versión se preparó en `tmp/tutor_revision_20260924/candidate.docx` y `candidate.pdf` y se exportó desde Microsoft Word mediante VBScript/COM.

### Integración de observaciones de la tutora

Se inspeccionaron los 22 comentarios del DOCX `TFG_GII_Alvaro_Osuna_Flores_REVISADO_201026.docx` y se resolvieron así:

- **64 — Introducción:** se concreta antes la dificultad metodológica y se reduce la densidad conceptual, conservando la motivación y las referencias pertinentes.
- **110 — Motivación:** se centra en por qué interesa estudiar la desinformación mediante un entorno experimental reproducible; detalles de método y límites se sitúan en sus capítulos.
- **197 — `fake_news`:** se distingue la etiqueta identificadora como código (`Consolas`); no se aplica cursiva a una etiqueta técnica.
- **199 — `fact-checking`:** se aplica cursiva al extranjerismo en las apariciones formateadas.
- **379 — Decisiones de diseño:** se conserva una introducción narrativa breve y se añade la tabla de decisión, justificación y cautela.
- **419 — `test_size`:** el parámetro queda identificado como código; los detalles operativos se documentan en metodología.
- **524 — Bibliografía:** se amplía a 28 obras pertinentes integradas en el texto y se conserva una entrada única por obra.
- **530 — Tabla B.1:** se mantienen las líneas horizontales superior, de cabecera y final solicitadas.
- **596 — Tabla B.2:** se aplica el formato horizontal uniforme.
- **622 — Tabla B.3:** se aplica el formato horizontal uniforme y la tabla queda completa en página.
- **651 — Tabla C.1:** se aplica el formato horizontal uniforme.
- **679 — Tabla C.2:** se aplica el formato horizontal uniforme.
- **711 — Tabla C.3:** se aplica el formato horizontal uniforme.
- **749 — Tabla D.1:** se aplica el formato horizontal uniforme.
- **783 — Tabla D.2:** se aplica el formato horizontal uniforme y se actualizan sus referencias al baseline histórico.
- **812 — Tabla D.3:** se aplica el formato horizontal uniforme y se delimitan sus referencias al protocolo histórico.
- **841 — Tabla E.1:** se aplica el formato horizontal uniforme y se distingue el inventario histórico de la suite actual.
- **871 — Tabla E.2:** se aplica el formato horizontal uniforme.
- **897 — Tabla F.1:** se aplica el formato horizontal uniforme.
- **952 — Tabla F.2:** se aplica el formato horizontal uniforme.
- **982 — Tabla F.3:** se aplica el formato horizontal uniforme.
- **1011 — Tabla F.4:** se aplica el formato horizontal uniforme; cabecera repetida y tabla íntegra.

También se atendieron las recomendaciones del correo: el contexto separa principios generales de detalles de implementación; se define la transformación `false`/`pants-fire` y la pérdida de granularidad; `no_fake` identifica la clase negativa sin certificar veracidad; se documentan exclusiones y duplicados antes de particionar; se amplía la comparación de trabajos y se incluye el presente TFG; se normaliza «conjunto de datos» y se desarrollan las siglas en su primera explicación útil. Los cambios de introducción, motivación y conclusiones se adaptaron al nuevo experimento. El Word de la tutora conserva su hash original y no se sobrescribió.

### Protocolo implementado y evidencia experimental

- Se restauró la búsqueda MinHash sobre todas las secuencias completas de cinco palabras, con 128 permutaciones, semilla 42, LSH de 32 bandas por cuatro filas, confirmación Jaccard ≥ 0,90 y procesamiento por lotes. Se retiraron la selección de fragmentos y el límite de 64 shingles.
- Los textos exactos conservan el representante de menor `source_id`; se mantiene la auditoría fila a fila. Los componentes de casi duplicados se agrupan antes de excluir componentes con etiquetas contradictorias. Las variantes retenidas comparten grupo y la clase negativa derivada se denomina `no_fake`.
- Los ejecutores y archivos incorporados son `scripts/run_robustness_experiments.py`, `configs/robustness_config.json`, `configs/robustness_protocol.md` y `tests/test_robustness_experiments.py`. El protocolo está documentado antes de la ejecución como protocolo fijado, no se denomina retrospectivamente prerregistrado. Las nueve ejecuciones exploratorias previas se conservan y no se usan como resultados principales.
- La ejecución completa identificada es `robustness-1a94400d502b149f`. Conserva preparación, asignaciones, modelos, predicciones, duraciones, métricas, versiones y huellas bajo `reports/robustness_runs/` y `data/derived/robustness/`; la configuración y el código tienen identidades separadas. Telegram no se incorpora a la preparación ni a los experimentos.
- De 50.503 filas originales se conservaron 44.408 representantes: 6.090 filas fueron redundantes exactas y cinco filas pertenecientes a dos componentes se excluyeron por conflicto. Por fuente: archive2, 44.898 → 38.826 representantes, 6.070 duplicados y dos exclusiones; LIAR, 5.605 → 5.582 representantes, 20 duplicados y tres exclusiones. El corpus derivado contiene 22.975 `no_fake` y 21.433 `fake_news`. Se confirmaron 42 grupos de casi duplicados y 45 aristas; no se detectaron grupos combinados entre ambas fuentes. LSH es una búsqueda aproximada y no garantiza detectar todas las paráfrasis.
- En las cinco particiones agrupadas, la regresión logística obtuvo macro F1 medio 0,9392 y desviación estándar muestral 0,0013; Linear SVC obtuvo 0,9388 ± 0,0020. La comparación principal usa la media de macro F1 para elegir entre esos candidatos en los mismos folds; no se interpreta como prueba independiente posterior a selección. Se conservaron matrices y métricas globales y por fuente.
- En la transferencia archive2 → LIAR los macro F1 fueron 0,5069 (regresión logística) y 0,5064 (Linear SVC); en LIAR → archive2 fueron 0,4741 y 0,5203, respectivamente. Estas cifras describen las fuentes y el protocolo actuales; no validan Telegram ni otros dominios.
- El macro F1 de 0,9424 queda únicamente como baseline histórico de una partición. Se mantiene su `run_id`, métricas, matriz y predicciones en el Apéndice H. Se documenta el solapamiento de textos normalizados detectado entre particiones; debido a las diferencias entre corpus y protocolos, no se atribuye causalmente una diferencia de rendimiento a la deduplicación.
- La suite ejecutada el 24/09/2026 informa **28 pruebas superadas, 0 fallidas y 0 errores** en 4,80 s. El informe JUnit está en `reports/robustness_runs/robustness-1a94400d502b149f/pytest_junit.xml`; **12** pruebas cubren el protocolo de robustez y 16 corresponden al conjunto anterior. La mención previa a diez pruebas nuevas fue errónea. Las pruebas técnicas no demuestran validez estadística ni generalización.
- La redistribución usada como archive2 se identifica mediante el registro conservado de descarga, la ficha de Kaggle `https://www.kaggle.com/datasets/emineyetm/fake-news-detection-datasets` (ID 2712039) y el conjunto original ISOT del grupo de investigación de University of Victoria, descrito en `https://onlineacademiccommunity.uvic.ca/isot/wp-content/uploads/sites/7295/2023/02/ISOT_Fake_News_Dataset_ReadMe.pdf`. La licencia de la copia redistribuida y la procedencia exacta de cada registro permanecen sin confirmar; la memoria no atribuye licencia.

### Verificación actual de los entregables temporales

- El PDF exportado por Word contiene **70 páginas físicas**, 55 marcadores de navegación, nueve imágenes y ninguna página sin contenido. El DOCX contiene 43 tablas editables, no tiene marcas de inserción/eliminación ni comentarios pendientes y conserva la portada del curso **2026-2027**.
- Se revisaron las hojas de contacto del documento y a tamaño legible las páginas afectadas, incluidas la Tabla 1, las Tablas 6, 10, 14, B.3, F.4 y H.1–H.4, las conclusiones y los apéndices G–H. Se confirmó que la Tabla 1 cabe completa en una página; las tablas cortas que no cabían se pasaron enteras a página nueva; no se redujo la fuente de tabla por debajo de 10 pt. La Tabla H.4 ocupa una página final con espacio libre amplio, consecuencia de mantener íntegros los resultados históricos y la paginación de anexos.
- El índice se actualizó desde Word. La frase histórica de Linear SVC se conserva literalmente en el contexto del baseline; el resumen y el capítulo de resultados presentan como principal la validación agrupada nueva. La redacción limita la validez al corpus archive2+LIAR y no atribuye resultados a Telegram.
- SHA-256 de los originales: DOCX `46d4d1fa163f1d432639a31a15bf3f5820db65f57c6bf1a8b98835cff24d3399`; PDF `a2575833d69b947b8bc27cb63210d79f8e0aac5bf094d28e362e875758749180`. El DOCX recibido de la tutora conserva `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`. No se sobrescribieron los originales.
- Antes de publicar esa versión se cotejaron texto, bibliografía, índice, cobertura visual, ausencia de revisiones pendientes, paginación y hashes de los archivos temporales. La afirmación anterior de que faltaban los originales era incorrecta: permanecen en `docs/` y sus hashes se han recalculado en la revisión integral del 01/10/2026.

**Estado del cierre experimental:** protocolo, ejecución, pruebas y revisión editorial completos. Los tres entregables de revisión se publican juntos después de verificar la correspondencia DOCX/PDF; originales y Word recibido preservados.

## Corrección de formato — 01/10/2026

- Se regeneró la copia temporal desde la revisión anterior conservada y se corrigió el tratamiento de identificadores y extranjerismos: `Consolas` se limita a `fake_news`, `no_fake` y `test_size`; la cursiva se aplica únicamente a `fact-checking` y a las etiquetas `Nota.` cuando corresponde. Los fragmentos contiguos mantienen la tipografía del cuerpo.
- Se normalizó la prosa de capítulos y apéndices a Times New Roman 12 pt, justificación, interlineado 1,5 y 6 pt posteriores. Se conservaron las excepciones de portada, objetivos, títulos, leyendas, notas, bibliografía, código y tablas; las celdas mantienen Times New Roman 10 pt e interlineado sencillo.
- Se ajustó la paginación del apartado 4.9 para mantener juntos sus dos párrafos finales y conservar el comienzo del capítulo 5 en página nueva. No se modificó el contenido de esos párrafos.
- Comparación estructural de la revisión temporal con la versión publicada antes de esta corrección: 509 párrafos y 43 tablas con texto idéntico; nueve imágenes insertadas con los mismos hashes y orden. Se mantienen el título, las cifras, las 28 referencias, los resultados, las tablas, las figuras, las conclusiones y la exclusión de Telegram del corpus y de la evaluación.
- Word actualizó los campos y el índice y exportó el PDF temporal con 55 marcadores. La exportación contiene 70 páginas; solo la portada tiene menos de 500 caracteres extraídos, no hay revisiones ni comentarios pendientes, y se reinspeccionaron en detalle las páginas 33–35 y 68–70 tras el último ajuste de paginación. Las páginas restantes se revisaron visualmente en la exportación completa.
- Esta corrección no ejecutó pruebas, entrenamientos, extracciones ni cálculos de métricas. El informe de 28 pruebas y los resultados experimentales conservan el alcance histórico que se describe en la sección de cierre del 24/09/2026.
- Se guardó una copia temporal de los archivos publicados antes de sustituirlos. Los hashes DOCX `C490269AC79952E725274ADB944A9CBA36D5F9DBD9DA908672BE5E25135568D1` y PDF `F4D552A0E1F7B893087C240CEEE7F71BB53EB9F5DB59225D47C514305121B599` identifican aquella versión anterior, no la revisión integral posterior. El documento de la tutora conserva el SHA-256 `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`. La afirmación de que los originales faltaban era incorrecta y queda rectificada; no se modificaron código, datos, modelos ni resultados.

## Revisión integral APA y redistribución — 01/10/2026

Esta sección describe la versión vigente y sustituye las referencias anteriores a 43 tablas, ocho apéndices, 70 páginas, celdas de 10 pt y «diez pruebas nuevas». Se trabajó sobre la copia de la revisión publicada en `tmp/apa_reorg_20261001/published_backup.docx`; el DOCX y PDF anteriores quedaron respaldados en el mismo directorio antes de cualquier sustitución.

### Correspondencia de tablas y contenido

Las antiguas tablas principales 1–16 pasan, respectivamente, a 1, 2, 3, 4, 6, 7, 8, 13, 15, 17, 19, 21, 22, 23, 24 y 25. Las tablas 1–4 mantienen su contenido; las tablas 7, 13, 15, 19 y 24 incorporan los datos únicos de tablas anteriores de los apéndices. La tabla 19 transpone la comparación de modelos. El cuerpo contiene ahora 25 tablas y el único Apéndice A histórico contiene cinco.

| Tabla anterior | Destino actual | Tratamiento de la información |
| --- | --- | --- |
| A.1 y D.1 | A1 | Configuración del baseline histórico fusionada. |
| B.1 | 5 (3.6) | Esquema canónico ampliado con los campos de auditoría del corpus derivado y `label_name=no_fake`. |
| B.2 | 7 (4.1) | Integrada en los criterios de inclusión; se conservan los recuentos por fichero y etiqueta. |
| B.3 | 10 (4.1) | Fases de construcción actualizadas al corpus derivado. |
| C.1 y C.3 | 12 (4.2) | Controles estructurales y límites semánticos consolidados. |
| C.2 | 13 (4.3) | Transformaciones y evidencia fusionadas con las reglas de preprocesamiento. |
| D.2 | 15 (4.6) | Catálogo de artefactos actuales e históricos sin atribuir resultados antiguos al run nuevo. |
| D.3 | 17 (4.7) | Protocolo de reproducción y recuperación; los hashes actuales se muestran en la tabla 16. |
| E.1, E.2 y G.7 | 18 (4.9) | Cobertura de las 28 pruebas del JUnit: 16 anteriores y 12 de robustez. |
| F.1 | A5 | Catálogo de términos y pesos del baseline histórico, sin reinterpretarlo como modelo actual. |
| F.2, F.3 y F.4 | 4.6, 5.4, 5.5 y 5.8 | Cautelas sobre pesos, errores y artefactos integradas en la prosa; catálogo operativo en la tabla 15. |
| G.1 | 9 (4.1) | Conciliación final de representantes, duplicados exactos y conflictos por fuente. |
| G.2 | 11 (4.1) | Parámetros completos de MinHash, Jaccard y agrupación. |
| G.3 | 20 (5.1) | Macro F1, tamaño y duración de cada fold. |
| G.4 | 19 (5.1) | Medias, desviación estándar, OOF e iteraciones fusionadas con la comparación principal. |
| G.5 | 24 (5.6) | Cuatro transferencias, con columnas adaptadas a 12 pt. |
| G.6 | 16 (4.6) | Identidad criptográfica de la ejecución principal. |
| H.1, H.2 y H.3 | A2, A3 y A4 | Comparación, métricas por clase y matriz del baseline histórico. |
| H.4 | 5.4 | Patrones de error históricos descritos expresamente como cualitativos, sin atribución al run actual. |

La configuración efectiva del protocolo agrupado se incorpora en la tabla 14. La tabla 8 mantiene el resumen auditado del corpus; la tabla 9 diferencia los 6.090 estados finales de duplicado exacto de las 6.092 fusiones observadas en una etapa intermedia. La tabla 12 añade duplicación textual, idioma y banderas de calidad sin confundir controles técnicos con veracidad. Los párrafos extensos de los antiguos apéndices se trasladaron a los apartados temáticos; el Apéndice A conserva una introducción breve y solo resultados históricos. Todas las menciones e índice se actualizaron según la nueva secuencia 1–25 y A1–A5.

### Formato APA y coherencia científica

- Todas las celdas de las 30 tablas editables están a 12 pt. Se aplicaron 0,5 pt a la línea superior, a la separación bajo cabecera y a la inferior; no hay bordes verticales ni separadores ordinarios entre filas. Los márgenes interiores son 3 pt arriba y abajo y 5 pt a los lados; filas indivisibles y encabezado repetido en tablas multipágina. Cada tabla ocupa como máximo 15,8 cm. Número en negrita, título en cursiva y nota posterior alineados a la izquierda; solo «Nota.» aparece en cursiva. Las cifras comparables se alinearon a la derecha y los encabezados al centro.
- La tabla 24 usa «Dirección» y dedica más espacio al modelo y al tamaño de entrenamiento; la tabla 5 evita cortar los identificadores del esquema. La tabla 15 ensancha los nombres de artefactos. Se retiraron saltos de página heredados que aislaban los apartados 4.7 y 5.4 y se alinearon las notas de figura a la izquierda.
- Se mantienen nueve imágenes con hashes de medios idénticos a los de la revisión anterior. Las 28 referencias continúan en una lista única, alfabética y con sangría francesa. Se corrigió el orden Kapoor/Kaufman, el de tres citas múltiples y la cursiva de los números de fascículo; las 28 obras tienen mención en el texto y no se incorporaron referencias sin citar.
- El resultado principal corresponde a `robustness-1a94400d502b149f`: 44.408 representantes, cinco folds agrupados y macro F1 medio 0,9392 ± 0,0013 de regresión logística. El macro F1 0,9424 de Linear SVC se mantiene exclusivamente como referencia histórica en el Apéndice A y en su delimitación en el cuerpo. No se modificaron valores, matrices, predicciones, modelos ni artefactos. Telegram continúa fuera del corpus, el ajuste y la evaluación.
- La portada conserva el curso 2026-2027. La licencia de la redistribución `archive2` y la procedencia individual de sus registros permanecen sin confirmar; no se atribuye licencia. La carpeta `documentacion_referencia` sí existe en la raíz `TFGs` y contiene, entre otros materiales, la guía APA y la normativa ETSII. Quedan rectificadas las afirmaciones previas sobre su ausencia y sobre la ausencia de los originales.

### Validación de esta versión

- Word actualizó campos e índice y exportó la copia temporal. El PDF tiene **66 páginas**, 48 marcadores de navegación, nueve imágenes y ninguna página en blanco. Se revisaron visualmente todas las páginas; con detalle las tablas multipágina 5, 7, 12, 15, 18, 20 y A1–A5, las leyendas, el índice, la bibliografía y las transiciones entre capítulos. No se observaron recortes ni solapamientos; la comprobación geométrica de los bloques de texto e imágenes tampoco detectó desbordamientos.
- El DOCX temporal contiene 25 tablas principales y cinco históricas, sin inserciones o eliminaciones controladas ni comentarios pendientes. Las 30 tablas tienen sus rótulos y, cuando son necesarias, notas en el orden correcto; las tablas 15 y 17 se explican mediante la prosa que las sigue y no requieren nota independiente. Las filas no se parten y la cabecera se repite cuando procede. Las nueve imágenes conservan los mismos hashes de contenido que en el DOCX previo.
- El JUnit existente documenta **28 superadas, 0 fallidas, 0 errores**: 16 casos anteriores y 12 de robustez. No se ejecutaron pruebas nuevas, entrenamientos, extracciones ni cálculos de métricas en esta actuación. Las cifras publicadas se contrastaron con el manifiesto y las tablas del run conservado.
- Hashes SHA-256 de originales recalculados: DOCX `46D4D1FA163F1D432639A31A15BF3F5820DB65F57C6BF1A8B98835CFF24D3399`; PDF `A2575833D69B947B8BC27CB63210D79F8E0AAC5BF094D28E362E875758749180`. Word de la tutora: `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`. Ninguno se modificó.
- Los hashes DOCX `CDBCFB55BF4DD4D3E0BD51B21ED8BC2D4F4EA068DBC532850ABE8493D36133C1` y PDF `B7DEB163455A6467BF3B5E79552A3F402FCCFE22812D0D4D1732E77FD7A32945` identifican la versión de esta revisión publicada el 01/10/2026, antes de la corrección de tablas del 02/10/2026.

## Corrección de tablas y auditoría formal — 02/10/2026

- Se conservó en `tmp/table_alignment_20261002/` una copia de los tres entregables publicados antes de actuar. Se editó el DOCX de revisión en una copia temporal y se actualizaron campos e índice mediante una instancia nueva de Microsoft Word antes de exportar el PDF temporal.
- Se aplicó una regla de alineación por columna a las 30 tablas: los valores mixtos de las tablas 8 y A1 parten del mismo margen izquierdo; las columnas numéricas alinean los valores a la derecha. Los doce pesos, positivos y negativos, de la tabla A5 tienen las seis cifras decimales y la coma alineadas en el PDF. Los encabezados permanecen centrados.
- La tabla 9 conserva 15,8 cm de ancho y distribuye sus cinco columnas en 2,3 / 3,0 / 3,7 / 3,5 / 3,3 cm. «Representantes» aparece completo en una línea. Se comprobó automáticamente que ningún encabezado de una sola palabra se parte en las 30 tablas exportadas.
- El título de la tabla 6 es ahora «Decisiones de diseño y cautelas metodológicas». Se añadieron menciones previas a las figuras 4 y 5 y a las tablas históricas A1–A4; la tabla A5 ya estaba citada. No cambió el contenido de ninguna celda ni se alteró ninguna cifra, figura o referencia bibliográfica.
- La auditoría estructural confirmó los bordes horizontales de 0,5 pt, la ausencia de bordes verticales e interiores ordinarios, los anchos dentro de 15,8 cm, el número en negrita, el título en cursiva, las filas indivisibles y las cabeceras repetibles de las 30 tablas. APA 7 permite omitir notas de tabla cuando no añaden información necesaria: las tablas 15 y 17 se explican en la prosa inmediata. Se conservan A4, márgenes de 2,5 cm, cuerpo y tablas Times New Roman 12 pt e interlineados institucionales.
- El PDF final tiene **66 páginas**, 48 marcadores y nueve imágenes; no contiene páginas vacías, texto fuera de página ni texto de cuerpo reducido por debajo de 12 pt. Se cotejaron visualmente las 66 páginas con la versión previamente revisada: 57 páginas fueron idénticas al raster y se inspeccionaron a tamaño legible las nueve modificadas (9, 25, 27, 28, 36, 38, 58, 64 y 66). Las tablas 8, 9, A1 y A5, las figuras referidas, conclusiones, bibliografía e índice quedaron legibles, sin cortes ni solapamientos.
- La comparación de DOCX antes y después identificó únicamente cuatro cambios de texto en párrafos: el título de la tabla 6 y las tres menciones añadidas. Las 30 tablas conservan idéntico texto en sus celdas y las nueve imágenes conservan sus hashes. Las 28 referencias, las cifras experimentales y la separación de Telegram respecto al corpus y la evaluación no cambiaron. El informe JUnit existente contiene 28 pruebas, 0 fallos y 0 errores; no se ejecutaron pruebas ni experimentos nuevos durante esta corrección.
- SHA-256 de los originales, de nuevo comprobados: DOCX `46D4D1FA163F1D432639A31A15BF3F5820DB65F57C6BF1A8B98835CFF24D3399`; PDF `A2575833D69B947B8BC27CB63210D79F8E0AAC5BF094D28E362E875758749180`. El Word recibido de la tutora conserva `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`.
- Hashes de los entregables DOCX/PDF validados para publicación: `65A717F8B1D5227F2E70575B5A8B4E17459260AC9B8C8DE6F8F7B2B58E65A701` y `1822CE7295ECC61151E3CE5B4A3958F4F1C7DC661D5C6ECA7639D39FE53CE53C`, respectivamente. Solo se sustituyen el DOCX y PDF de revisión y este registro.

## Integración fiel de la revisión de Liliana — 15/10/2026

### Documento de partida y criterio de integración

- Se tomó como fuente editorial el DOCX recibido `TFG_GII_Alvaro_Osuna_Flores_REVISADO_201026 (1).docx` (SHA-256 `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`). Se creó una copia de trabajo, se aceptaron en ella las **499 revisiones de texto y formato** y se inventariaron sus **22 comentarios**. El archivo recibido permanece intacto.
- Para conservar la organización y las tablas de la fase experimental posterior, la entrega se montó en una copia de la maquetación de revisión vigente, cotejando y trasladando el texto de la vista aceptada de Liliana. Una reconstrucción física mediante copia de grandes rangos formateados del Word recibido produjo un documento inestable al exportar y no se publicó. Esta diferencia de procedimiento no equivale a descartar sus correcciones: se cotejaron explícitamente los pasajes y comentarios indicados abajo.
- El resumen final vuelve a los **cinco párrafos** de la tutora: se conservan su planteamiento inicial, propósito y cierre; los párrafos de método y resultado se adaptan al run posterior. Se recuperan los **cinco párrafos de introducción**, los **cinco de motivación**, el objetivo general, los **siete específicos** y los **nueve párrafos de conclusiones**. Se corrigieron erratas inequívocas de las inserciones (`ste`, `fake new`, `conjunos`, `anaális`, «deducción» por «deduplicación») y se retiró el párrafo aislado compuesto por un punto. Los párrafos recuperados usan el cuerpo institucional, no estilos web ni de título.
- La adaptación sustantiva se limita a hechos posteriores al Word de Liliana: corpus derivado de **44.408** representantes; cinco particiones agrupadas; macro F1 medio **0,9392 ± 0,0013** de regresión logística frente a **0,9388 ± 0,0020** de Linear SVC; transferencias entre archive2 y LIAR; y 28 pruebas documentadas. El **0,9424** se conserva como baseline histórico de una sola partición. Telegram sigue separado del corpus, entrenamiento y evaluación, con pruebas simuladas pero sin acceso real acreditado.

### Resolución individual de los 22 comentarios

| Comentario | Resolución y localización en la memoria final |
| --- | --- |
| 64 | Reformulación editorial de la introducción recuperada en **1. Introducción**; resultados adaptados al protocolo agrupado. |
| 110 | Cinco párrafos de motivación recuperados en **1.1 Motivación**, sin presentar Telegram como objeto evaluado. |
| 197 | `fake_news` se trata como identificador y se distingue de la prosa en **2.3, 3.6, 4.1** y tablas. |
| 199 | *Fact-checking* se distingue tipográficamente como extranjerismo en **2.1 y 2.6**; no se aplica cursiva a palabras vecinas. |
| 379 | **3.8** conserva la síntesis narrativa y la **Tabla 6**, «Decisiones de diseño y cautelas metodológicas». |
| 419 | `test_size` se identifica como parámetro técnico; la configuración histórica se delimita en la **Tabla A1**. |
| 524 | Bibliografía única de **28 obras citadas**, conservada en **Bibliografía** y cotejada con el cuerpo. |
| 530 | El esquema canónico pasa a **3.6, Tabla 5**, con campos del corpus derivado y reglas de presentación horizontal. |
| 596 | Reglas de construcción e inclusión pasan a **4.1, Tablas 7 y 8**, sin duplicar cifras. |
| 622 | Conciliación y agrupación pasan a **4.1, Tablas 9–11**, con bordes horizontales y encabezados legibles. |
| 651 | Controles y límites estructurales pasan a **4.2, Tabla 12** y su explicación. |
| 679 | Transformaciones deterministas pasan a **4.3, Tabla 13** y su explicación. |
| 711 | La distinción entre calidad estructural y semántica se conserva en **4.2–4.3**. |
| 749 | Configuración del baseline anterior delimitada en el **Apéndice A, Tabla A1**. |
| 783 | Artefactos y trazabilidad del run principal se documentan en **4.6, Tablas 15–16**; los históricos quedan separados. |
| 812 | Protocolo de reproducción y sus límites pasan a **4.7, Tabla 17**. |
| 841 | Cobertura técnica de las pruebas se resume en **4.9, Tabla 18**; el resultado del JUnit se interpreta en **5.7**. |
| 871 | Se distingue la suite actual de **28** casos del registro anterior de **16** en **4.9 y 5.7**. |
| 897 | Términos y pesos del modelo anterior se conservan como evidencia histórica en **Tabla A5**. |
| 952 | Cautelas de lectura de los pesos se integran en **5.5** y la nota de **Tabla A5**. |
| 982 | Análisis de errores y límites de atribución se integran en **5.4 y 5.8–5.9**. |
| 1011 | Las cautelas de interpretación y de fuente se integran en **5.5–5.9**; la tabla histórica larga conserva cabecera y filas legibles. |

### Cotejo final y publicación

- El resultado conserva seis capítulos, ocho apartados de contexto, **25 tablas principales y cinco históricas en un único Apéndice A**, nueve imágenes y 28 referencias. El resumen y las conclusiones presentan el experimento agrupado como principal. El manifiesto `reports/robustness_runs/robustness-1a94400d502b149f/robustness_manifest.json` identifica el run completo y sus cifras; el JUnit del mismo directorio declara **28 pruebas, 0 fallos y 0 errores**. No se entrenó ni se ejecutó `pytest` en esta actuación.
- La copia final del DOCX contiene **cero revisiones y cero comentarios** en sus historias Word. Word actualizó campos e índice en la copia de trabajo. Su paginación interna fue de 68 páginas; la exportación PDF validada ocupa **67 páginas A4**, con **48 marcadores de navegación**, ninguna página en blanco, 30 tablas editables en el DOCX y nueve imágenes. Se renderizaron e inspeccionaron las 67 páginas, con examen adicional de portada, índice, resumen, tablas extensas, capítulo 5, conclusiones, bibliografía y Apéndice A. La única diferencia entre los dos PDF temporales previos fue el resultado visible del índice en las páginas 2–3.
- **Incidencia de exportación:** Word pudo actualizar y guardar los campos, pero sus tres vías probadas de salida a PDF quedaron bloqueadas al exportar copias editadas de esta memoria. Se utilizó LibreOffice para el PDF definitivo; por su diferente paginación desde 4.2, se ajustó el resultado en caché de 23 entradas del índice del DOCX para coincidir con las páginas reales del PDF. El campo sigue siendo actualizable en Word si se modifica de nuevo la memoria. No se afirmó falsamente una exportación final por Word.
- SHA-256 de la entrega validada: DOCX `33F939103A77A51375834EC92A0158F1E50B31C0D02ED689A02D176661C17C58`; PDF `401495F8502B127CD42D02F597FE7B304A3460FAFFE0A7D8BEBAD080C1B9E845`. Se respaldaron los entregables publicados previamente en `tmp/liliana_integration_20261015/` antes de sustituirlos.
- Los originales conservan SHA-256 DOCX `46D4D1FA163F1D432639A31A15BF3F5820DB65F57C6BF1A8B98835CFF24D3399` y PDF `A2575833D69B947B8BC27CB63210D79F8E0AAC5BF094D28E362E875758749180`; el Word de Liliana conserva el hash indicado arriba. No se modificaron código, datos, configuración, modelos, resultados ni artefactos experimentales.

## Corrección final de formato y fidelidad tipográfica — 15/10/2026

- Se respaldaron los tres entregables publicados antes de actuar en `tmp/format_fidelity_20261015/`. La versión anterior tenía hashes DOCX `33F939103A77A51375834EC92A0158F1E50B31C0D02ED689A02D176661C17C58` y PDF `401495F8502B127CD42D02F597FE7B304A3460FAFFE0A7D8BEBAD080C1B9E845`.
- La frase «Bidirectional Encoder Representations from Transformers» recupera exactamente la cursiva del Word aceptado de Liliana; la sigla BERT y las palabras contiguas quedan en redonda. Se cotejaron sus demás cursivas identificables con el DOCX recibido. Los extranjerismos en prosa se distinguen de identificadores, parámetros, rutas y etiquetas, que conservan formato de código; los títulos de obras y las palabras clave se respetan según su función documental. No se aplicó una normalización global de los párrafos.
- Se corrigieron **25 párrafos** del cuerpo y del apéndice que heredaban interlineado 1,15 y 10 pt posteriores; ahora siguen el patrón institucional de Times New Roman 12 pt, justificación, interlineado 1,5 y 6 pt posteriores. Otros **28 párrafos** recuperaron la justificación. Los cambios de formato de carácter se limitaron a los fragmentos pertinentes, conservando las propiedades de los demás tramos, campos, enlaces y marcadores. Se equilibró la página del resumen sin modificar sus cinco párrafos ni la línea de palabras clave.
- La Tabla 24, de transferencias, recibió un ajuste localizado de anchuras: el nombre «Regresión logística» queda separado del recuento adyacente y «Entrenamiento» ya no se parte dentro de la palabra. Su texto, cifras, precisión decimal, bordes y alineaciones permanecen intactos. Se revisaron las 30 tablas y sus continuaciones, las leyendas y notas, las figuras y las 28 referencias; se conservaron las cabeceras repetibles y el formato de 12 pt de las celdas.
- La comparación estructural con la versión anterior confirmó idéntico texto en todos los párrafos no vacíos y en las 30 tablas, **nueve imágenes** y **28 referencias**. No se alteraron objetivos, conclusiones, métricas, matrices, figuras ni el alcance: el experimento agrupado continúa como resultado principal, el macro F1 histórico de 0,9424 está delimitado y Telegram permanece fuera del corpus, entrenamiento y evaluación. No hay comentarios ni revisiones pendientes.
- Se intentó primero actualizar y exportar mediante Word en una copia temporal, pero la operación quedó bloqueada. La salida validada se obtuvo mediante LibreOffice. Se sincronizaron **38 entradas en caché** del índice con las páginas impresas del PDF y se cotejaron sus **48 marcadores**. El campo del índice sigue siendo actualizable en Word; una futura reexportación con otro motor requiere comprobar de nuevo la paginación.
- Se renderizaron y revisaron visualmente las **69 páginas A4** a tamaño legible, con atención a portada, resumen, BERT, tablas multipágina, capítulo 5, conclusiones, bibliografía y Apéndice A. No se detectaron páginas en blanco, recortes ni texto fuera de los límites de página. La corrección localizada de la Tabla 24 se volvió a exportar e inspeccionar. El PDF supera el mínimo de 63 páginas sin reducir el cuerpo para ajustar la extensión.
- Hashes SHA-256 de esta entrega: DOCX `347966841542812C757A82EE76CB3C8B94998125CFCE81F059AA4CDC0739FF78`; PDF `E35508EFD64CDCC6CC9B9F1BB2A63BD73EF981EBB7F5B0058776B29E0ECBEA96`. Los originales permanecen en DOCX `46D4D1FA163F1D432639A31A15BF3F5820DB65F57C6BF1A8B98835CFF24D3399` y PDF `A2575833D69B947B8BC27CB63210D79F8E0AAC5BF094D28E362E875758749180`; el Word de Liliana conserva `D121AE7A627036B2500DEE2EF34C30155C03A35C2343852123E05A704A673D49`. No se modificaron código, datos, configuración, modelos, resultados ni artefactos experimentales.
