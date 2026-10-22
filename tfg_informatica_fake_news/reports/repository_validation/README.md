# Comprobación del repositorio del 22 de octubre de 2026

La comprobación se ejecuta en un entorno virtual nuevo con Python 3.11.9 y `requirements-reproducible.txt`. Se mantiene aparte del JUnit y del manifiesto experimental de septiembre.

- `pytest_20261022.xml`: 33 pruebas superadas, cero fallos. Son las 28 pruebas previas y cinco añadidas para restauración e integridad del paquete.
- `integrity_20261022.json`: hashes de 51 archivos directos y 17 artefactos restaurados, correspondencia de métricas y matrices, cobertura de 44.408 predicciones OOF por modelo, partición de grupos y conciliación de las 50.503 filas originales.
- `clean_checkout_20261022.json` y `clean_checkout_tests_20261022.xml`: comprobación desde una exportación limpia del índice de Git, sin utilizar los directorios locales ignorados.
- `model_inference_20261022.json`: carga de los 14 modelos restaurados y contraste de 42 predicciones, puntuaciones y umbrales guardados, tres ejemplos por modelo, en la copia limpia.

Se ejecutan las pruebas, `pip check`, los modos `--dry-run` y la inferencia de muestra con modelos persistidos. La comprobación de cifras usa predicciones ya guardadas; no vuelve a entrenar el corpus ni modifica sus resultados. Las pruebas de Telegram utilizan un cliente simulado.
