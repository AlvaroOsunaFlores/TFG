# Pipeline experimental reproducible para clasificación de fake news

Este TFG de Ingeniería Informática estudia la construcción y validación de un corpus binario, su auditoría de duplicados y la comparación de clasificadores lineales TF-IDF. El experimento principal utiliza exclusivamente archive2 y LIAR. Telegram es un módulo complementario: sus mensajes no participaron en el corpus, entrenamiento ni evaluación.

La entrega incluye código, configuraciones, datos de entrada, corpus derivado, particiones, predicciones, métricas y modelos del experimento documentado. Los modelos y los CSV más grandes se distribuyen comprimidos; un comando los restaura con sus bytes originales y comprueba sus SHA-256.

## Empezar

La [guía de reproducción](docs/REPRODUCIBILIDAD.md) explica instalación, comprobación, ejecución completa y recuperación. El entorno de referencia usa Python 3.11.9.

Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reproducible.txt
.\.venv\Scripts\python.exe -m scripts.restore_artifacts
.\.venv\Scripts\python.exe -m scripts.verify_reproducibility --check-results
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json --dry-run
```

En Linux/macOS se usa `.venv/bin/python`. Estas comprobaciones y el entrenamiento no requieren credenciales de Telegram. El último comando solo muestra la identidad y el protocolo. Para repetir el experimento completo:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json
```

La configuración de reproducción conserva los parámetros científicos y escribe en otros directorios. La configuración original y los artefactos publicados se mantienen como referencia de la memoria.

## Experimento principal

Run: `robustness-1a94400d502b149f`. El [manifiesto completo](reports/robustness_runs/robustness-1a94400d502b149f/robustness_manifest.json) contiene las cifras exactas.

- Entrada: 50.503 registros, 44.898 de archive2 y 5.605 de LIAR.
- Auditoría final: 44.408 representantes, 6.090 duplicados exactos y cinco exclusiones por conflicto; son estados mutuamente excluyentes.
- Corpus derivado: 22.975 `no_fake` y 21.433 `fake_news`.
- Casi duplicados: todos los shingles de cinco palabras, MinHash de 128 permutaciones, semilla 42, LSH 32 × 4 y confirmación Jaccard ≥ 0,90. Las variantes coherentes permanecen bajo un mismo grupo.
- Cinco particiones `StratifiedGroupKFold` comunes a ambos modelos; vectorizador y clasificador se ajustan solo con entrenamiento.
- Umbrales fijos: 0,60 para probabilidad de regresión logística y 0,30 para `decision_function` de LinearSVC.

| Comparación interna | Macro F1 medio | Desviación estándar muestral |
| --- | ---: | ---: |
| Regresión logística | 0,9392 | 0,0013 |
| Linear SVC | 0,9388 | 0,0020 |

La selección sobre los mismos cinco folds es una comparación interna. No constituye una estimación independiente posterior a seleccionar el modelo ni demuestra significación estadística de la pequeña diferencia.

## Transferencia y límites de generalización

| Entrenamiento → prueba | Regresión logística: macro F1 | Linear SVC: macro F1 |
| --- | ---: | ---: |
| archive2 → LIAR | 0,5069 | 0,5064 |
| LIAR → archive2 | 0,4741 | 0,5203 |

Las transferencias son evidencia especialmente relevante de las limitaciones de generalización: el rendimiento interno no se mantiene al cambiar de fuente. Formato, longitud, anotación y estilo editorial cambian conjuntamente; el experimento no aísla una causa única. El macro F1 OOF de regresión logística difiere por fuente: 0,9845 en archive2 y 0,5949 en LIAR.

Se distinguen rendimiento interno, transferencia entre estas dos fuentes y capacidad de detección en otros dominios. No se ha validado esta última en Telegram. `no_fake` es la clase negativa heredada y no acredita verificación factual independiente. La búsqueda LSH es aproximada y puede omitir paráfrasis.

## Referencia histórica

El run `baseline-20260411T145313Z-a9ea359a` obtuvo macro F1 0,9424 con Linear SVC en un holdout de 12.626 registros. Sus [artefactos](reports/training_runs/baseline-20260411T145313Z-a9ea359a) se conservan como evidencia histórica. Una auditoría posterior identificó solapamiento de textos normalizados entre entrenamiento y holdout. La comparación con el nuevo protocolo no mide un efecto causal aislado de deduplicar.

`verificado_o_neutro` se conserva únicamente al describir el corpus y los resultados históricos. Las ejecuciones exploratorias no se publican como experimentos finales.

## Archivos y evidencia

| Ubicación | Contenido |
| --- | --- |
| `configs/robustness_config.json` y `configs/robustness_protocol.md` | Configuración original y protocolo del run principal. |
| `configs/robustness_reproduction.json` | Mismos parámetros con directorios de salida diferentes. |
| `requirements-reproducible.txt` | Entorno fijado de comprobación; NumPy, pandas y scikit-learn coinciden con el run. |
| `data/labeled/` | Corpus canónico histórico, metadatos y muestra sintética. |
| `data/derived/robustness/robustness-1a94400d502b149f/` | Corpus derivado y auditoría restaurada. |
| `reports/robustness_runs/robustness-1a94400d502b149f/` | Manifiesto, estado, particiones, métricas, matrices, predicciones y transferencias. |
| `reproducibility/artifacts.json` y `reproducibility/archives/` | Inventario, hashes y compresión reversible de 14 modelos principales y evidencias adicionales. |
| `reports/repository_validation/` | Evidencia de comprobación del repositorio, separada del experimento. |
| `docs/CAMBIOS_REALIZADOS.md` | Historial editorial y resolución de comentarios. |

Memoria vigente: [DOCX](docs/TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.docx) y [PDF](docs/TFG_GII_Alvaro_Osuna_Flores_Pipeline_Fake_News_Memoria_REVISION.pdf). Los Markdown anteriores de memoria y propuesta son históricos. `docs/Defensa/` reúne las presentaciones y vídeos disponibles, incluida la presentación v2; la versión que se utilice en la defensa debe contrastarse con el experimento principal.

## Pruebas y Telegram

El JUnit del run conserva 28 pruebas: 16 de componentes anteriores y 12 de robustez. Las cinco pruebas de restauración e integridad añadidas para esta entrega se documentan en el informe actual de comprobación del repositorio.

Telegram se comprueba mediante `_FakeClient`; no acredita acceso real, monitorización continua ni eficacia de clasificación en Telegram. La muestra local puede ejecutarse por separado con `python main.py --use-sample`; produce datos sin etiquetas y no alimenta el experimento supervisado.

## Procedencia

El corpus canónico versionado permite repetir el experimento sin nuevas descargas. Archive2 contiene `Fake.csv` y `True.csv`; la documentación conserva el identificador 2712039 y la [redistribución de emineyetm en Kaggle](https://www.kaggle.com/datasets/emineyetm/fake-news-detection-datasets), asociada a ISOT. La licencia de la copia disponible no está confirmada; no se atribuye licencia de redistribución.

LIAR se documenta en la [publicación de Wang de 2017](https://aclanthology.org/P17-2067/). Se incluyen `true`, `false` y `pants-fire` con binarización experimental; se excluyeron 7.184 categorías intermedias y dos registros vacíos en la construcción histórica. La reconstrucción opcional desde fuentes se explica en la guía.
