# Reproducción y auditoría del experimento

Esta guía permite comprobar las cifras publicadas y repetir el protocolo agrupado con los archivos del repositorio. El run principal es `robustness-1a94400d502b149f`; el baseline de abril es histórico. La comprobación de entrega del 22 de octubre de 2026 se conserva por separado en `reports/repository_validation/`.

## 1. Obtener el proyecto y preparar Python

```powershell
git clone --branch feat/separacion-tfgs https://github.com/AlvaroOsunaFlores/TFG.git
Set-Location TFG/tfg_informatica_fake_news
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reproducible.txt
.\.venv\Scripts\python.exe -m pip check
```

El entorno comprobado usa Python 3.11.9, NumPy 1.26.4, pandas 2.2.3 y scikit-learn 1.4.2. Estas tres bibliotecas coinciden con el manifiesto del experimento. Las demás versiones fijadas describen el entorno de comprobación de esta entrega; no se presentan como un registro histórico completo de septiembre.

En Linux/macOS, `python3.11 -m venv .venv` crea el entorno y `.venv/bin/python` sustituye a `.\.venv\Scripts\python.exe`. Los comandos siguientes se ejecutan desde `tfg_informatica_fake_news`. No se necesitan credenciales ni configurar `.env` para repetir el experimento.

## 2. Restaurar los artefactos grandes

```powershell
.\.venv\Scripts\python.exe -m scripts.restore_artifacts --dry-run
.\.venv\Scripts\python.exe -m scripts.restore_artifacts
```

Se distribuyen 17 gzip adicionales: los 14 modelos principales, la auditoría de 50.503 filas, las predicciones del holdout histórico y su modelo. Los corpus canónico y derivado ya se incluyen como CSV gzip en sus rutas de datos.

La restauración usa `reproducibility/artifacts.json`, comprueba el hash comprimido y el de los bytes extraídos y recupera las rutas relativas originales. Si un destino existe con otros bytes, lo conserva e informa del conflicto. Se puede repetir sin duplicar archivos correctos y solo requiere la biblioteca estándar de Python.

Los manifiestos históricos conservan rutas absolutas de la máquina original. Describen procedencia; el inventario y los comandos nuevos utilizan rutas relativas a la copia clonada.

## 3. Comprobar integridad y cifras guardadas

```powershell
.\.venv\Scripts\python.exe -m scripts.verify_reproducibility --check-results --report reports/local_verification.json
```

Se comprueban las huellas de corpus, configuración, ejecutor, particiones, modelos y predicciones. `--check-results` lee las predicciones guardadas y contrasta métricas y matrices globales, por fuente, por fold y de transferencia. También comprueba una predicción OOF por cada uno de los 44.408 registros y por modelo, y que cada grupo pertenezca a un único fold.

La conciliación final es 44.408 representantes, 6.090 duplicados exactos y cinco exclusiones por conflicto, sumando 50.503 originales. Las 6.092 fusiones intermedias no son otro total final.

Este comando recalcula métricas desde predicciones persistidas para cotejarlas; no ajusta modelos ni sustituye resultados. Una comprobación correcta acredita integridad y correspondencia de artefactos, no generalización a otras fuentes o a Telegram.

## 4. Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/local_tests.xml
```

El JUnit original conserva 28 casos. La comprobación del repositorio añade cinco pruebas de restauración, protección de destinos, integridad, rutas y cálculo de métricas. Los informes se distinguen por fecha y ubicación. Telegram se prueba con `_FakeClient`; esto no acredita credenciales, canales reales ni eficacia predictiva en Telegram.

## 5. Repetir el experimento completo

El protocolo conserva la deduplicación exacta con representante de menor `source_id`, todos los shingles de cinco palabras, MinHash de 128 permutaciones y semilla 42, LSH 32 × 4, confirmación Jaccard ≥ 0,90 y componentes previos a excluir conflictos. Las variantes coherentes quedan agrupadas, y los grupos mixtos se excluyen de transferencia cuando existen.

Los dos modelos usan las mismas cinco particiones estratificadas por grupo, TF-IDF de unigramas y bigramas ajustado solo en entrenamiento, máximo de 5.000 características, C = 1 y clases balanceadas. Regresión logística usa `lbfgs`; LinearSVC usa `dual=True`. Los umbrales permanecen en 0,60 y 0,30. La comparación usa macro F1 medio y desviación estándar muestral.

Primero se comprueba la identidad prevista:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json --dry-run
```

Después se lanza la preparación, los diez ajustes de validación cruzada y las cuatro transferencias:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json
```

Esta operación requiere más recursos que las pruebas y su duración depende del equipo. Solo cambian los tres directorios de salida respecto a la configuración histórica:

| Artefactos nuevos | Directorio |
| --- | --- |
| Corpus y auditoría | `data/derived/reproduction/<run_id>/` |
| Estado, predicciones, métricas y manifiesto | `reports/reproduction_runs/<run_id>/` |
| Catorce modelos | `models/reproduction_runs/<run_id>/` |

El hash de configuración cambia al cambiar rutas, generando otro identificador. La identidad incluye también la versión completa de Python, el sistema operativo y las versiones de NumPy, pandas y scikit-learn: otro entorno puede producir otro identificador. Duraciones, marcas de tiempo y bytes de un gzip nuevo pueden diferir aunque el protocolo y las filas sean equivalentes. Las métricas se comparan con precisión numérica.

Si se interrumpe, se usa el identificador de `--dry-run` o `run_state.json`:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json --resume <run_id>
```

La recuperación exige coincidencia de datos, código, configuración y versiones. Reutiliza únicamente etapas y ajustes completos con hashes compatibles. No se ejecutan dos procesos sobre el mismo run. Solo un manifiesto con `status=completed` identifica una ejecución terminada.

## 6. Fuentes y reconstrucción opcional

El corpus canónico incluido basta para repetir el experimento. Su SHA-256 es `cfaf1b39c0260008e9328950649c9b83de2a9eadb478f631fb9cbc68d1b0a6b1`. El corpus derivado original tiene SHA-256 `184c707840a4bcff72dbef5e75e179152b630395c5f63f072db969bc1e79ea4e`.

Las fuentes fueron `archive2.zip` (`Fake.csv` y `True.csv`) y `archive.zip` (LIAR). El identificador 2712039 corresponde a la redistribución de emineyetm en Kaggle, asociada a ISOT. La licencia de la copia disponible permanece sin confirmar y no se atribuye una nueva licencia.

En archive2, Fake se mapea a `fake_news` y True a la clase negativa. En LIAR, `false` y `pants-fire` se agrupan como positivos y `true` como negativo. Se excluyen 2.627 `half-true`, 2.454 `mostly-true` y 2.103 `barely-true`, además de dos filas sin texto útil. El nombre negativo histórico `verificado_o_neutro` pasa a `no_fake` en la versión derivada sin afirmar verificación independiente.

Si se dispone de ambos ZIP, se puede reconstruir en otras rutas para preservar el corpus histórico:

```powershell
.\.venv\Scripts\python.exe -m scripts.build_real_dataset --source-root C:/ruta/a/las/fuentes --output data/reconstructed/fake_news_unified.csv.gz --metadata-output data/reconstructed/fake_news_unified.metadata.json
```

Los metadatos documentan inclusiones, exclusiones, idioma detectado y huellas. Un esquema válido no demuestra calidad semántica de las etiquetas.

## 7. Interpretación

El resultado principal es macro F1 medio 0,9392 ± 0,0013 para regresión logística y 0,9388 ± 0,0020 para Linear SVC. La selección sobre los mismos folds es interna. Las transferencias entre fuentes presentan macro F1 entre 0,4741 y 0,5203: son evidencia relevante de limitaciones de generalización y no equivalen a capacidad de verificar noticias en un dominio nuevo. Telegram no interviene en estas evaluaciones.

El 0,9424 de Linear SVC pertenece al holdout histórico, cuyo solapamiento se documentó posteriormente. No se interpreta la diferencia entre protocolos como efecto causal aislado de la deduplicación.
