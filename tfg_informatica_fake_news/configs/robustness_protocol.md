# Protocolo de robustez fijado antes de la ejecución final

Fecha de fijación: 24 de septiembre de 2026. Este documento fija la ejecución final antes de generar sus métricas; no se atribuye retrospectivamente a las exploraciones anteriores.

## Datos y duplicados

- Entrada: `data/labeled/fake_news_unified.csv.gz`, cuya huella se registrará en el manifiesto.
- La etiqueta binaria nueva será `no_fake` (0) y `fake_news` (1). La primera expresa solo la clase negativa del experimento, no una verificación independiente.
- Los textos normalizados idénticos conservarán como representante el menor `source_id`; cada fila original quedará en el registro de auditoría.
- Para textos con al menos cinco palabras se construirán todos los *shingles* contiguos de cinco palabras. Los textos más cortos solo se considerarán duplicados si coinciden exactamente.
- La búsqueda aproximada utilizará MinHash con 128 permutaciones, semilla 42 y LSH con 32 bandas de cuatro filas. Los candidatos se confirmarán con Jaccard ≥ 0,90 sobre los *shingles* completos.
- Los componentes conexos se formarán antes de filtrar etiquetas. Se excluirá íntegramente cualquier componente que contenga más de una etiqueta; las variantes coherentes permanecerán en el corpus y compartirán grupo.
- Los componentes con procedencia de ambas fuentes quedarán fuera de la transferencia entre fuentes. La búsqueda aproximada puede omitir paráfrasis o duplicados que no compartan una banda LSH.

## Modelos y evaluación

- Se compararán regresión logística y LinearSVC con TF-IDF de unigramas y bigramas, `min_df=1`, `max_features=5000`, `C=1` y `class_weight=balanced`.
- Se mantendrán los umbrales configurados: 0,60 sobre probabilidad para regresión logística y 0,30 sobre la función de decisión de LinearSVC. No se optimizarán con las evaluaciones.
- LinearSVC utilizará `dual=True`; se registrarán tiempo, iteraciones, avisos de convergencia y versiones de bibliotecas.
- Validación cruzada: cinco particiones `StratifiedGroupKFold`, barajadas con semilla 42, que mantienen cada componente de duplicados en una sola partición. El vectorizador y el modelo se ajustarán dentro de cada partición con las filas de entrenamiento.
- La comparación principal será la media de macro F1 de las cinco particiones, acompañada de desviación estándar muestral y resultados por partición. Se informarán también métricas globales y por fuente sobre predicciones fuera de entrenamiento.
- Se evaluará transferencia en ambas direcciones (ISOT a LIAR y LIAR a ISOT), con los grupos de procedencia mixta excluidos en ambos sentidos.
- No se buscarán hiperparámetros, umbrales ni arquitecturas adicionales. La comparación de cinco particiones sirve para comparar modelos dentro de este protocolo; no constituye una evaluación externa independiente tras seleccionar un ganador.

## Aclaración de implementación

Las firmas MinHash se calculan por lotes de 256 documentos para limitar la memoria temporal; la confirmación Jaccard regenera las secuencias completas de cada pareja candidata. Regresión logística fija explícitamente `solver=lbfgs`; LinearSVC mantiene `dual=True` y el backend liblinear.

## Trazabilidad

Cada ejecución nueva tendrá un identificador derivado de las huellas del corpus, configuración, código y versiones. Se conservarán el corpus derivado, auditoría por registro, grupos, asignaciones de partición, predicciones, métricas, matrices, modelos y manifiesto. Una reanudación solo reutilizará artefactos cuyas huellas coincidan con el estado de ejecución.
