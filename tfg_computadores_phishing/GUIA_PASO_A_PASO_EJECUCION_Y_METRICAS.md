# Guia muy detallada: ejecucion, prueba y lectura de metricas

Este documento esta pensado para ejecutar el proyecto paso a paso sin suponer experiencia previa.

## 1) Que hace este proyecto

El proyecto:
- Lee mensajes de Telegram con Telethon.
- Limpia y analiza texto (idioma, tokens, lemas, entidades).
- Clasifica cada mensaje como:
  - `0` = benigno
  - `1` = amenaza/phishing
- Guarda resultados en MongoDB.
- Permite evaluar el modelo con un dataset de prueba (`data/test.csv`) y generar metricas.

## 2) Estructura minima del proyecto

Debes estar dentro de esta carpeta:

`TFG_MVP_TelegramIA_Mongo_v3`

Archivos clave:
- `main.py`: bot de Telegram en tiempo real.
- `evaluate.py`: evaluacion offline con dataset CSV.
- `model_loader.py`: carga robusta del modelo (formato Transformers o `.pt`).
- `requirements.txt`: dependencias Python.
- `docker-compose.yml` y `Dockerfile`: ejecucion con Docker.
- `.env.example`: plantilla de variables.
- `data/test.csv`: dataset de prueba.

## 3) Requisitos previos (Windows)

Necesitas:
- Python instalado (`python --version`).
- pip instalado (`pip --version`).
- Internet (para descargar librerias, modelos spaCy y modelo de Hugging Face).
- Opcional pero recomendado: Docker Desktop.

Para verificar rapido:

```powershell
python --version
pip --version
docker --version
```

## 4) Paso 1 - Configurar variables de entorno

Desde la carpeta del proyecto:

```powershell
Copy-Item .env.example .env
```

Abre `.env` y revisa estas variables:

```env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=tu_api_hash
TELEGRAM_PHONE=+34123456789
MONGO_URI=mongodb://mongo:27017/
HF_MODEL=alvaroosuna/distilbert_fast_fixed_labels
THRESHOLD=0.05
HF_BASE_MODEL=distilbert-base-uncased
HF_STATE_DICT_FILE=distilbert_fast_fixed_labels.pt
```

Notas:
- `TELEGRAM_*` solo es obligatorio para ejecutar `main.py`.
- Para `evaluate.py` no hace falta Telegram, pero si hace falta acceso al modelo HF.
- `HF_BASE_MODEL` y `HF_STATE_DICT_FILE` son importantes porque tu repo HF usa `state_dict` (`.pt`).

## 5) Paso 2 - Instalacion local de dependencias (recomendado para probar rapido)

### 5.1 Crear entorno virtual

```powershell
python -m venv .venv
```

### 5.2 Activar entorno virtual

```powershell
.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### 5.3 Actualizar herramientas base

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 5.4 Instalar dependencias del proyecto

```powershell
python -m pip install -r requirements.txt
```

### 5.5 Instalar modelos spaCy requeridos por `main.py`

```powershell
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```

## 6) Paso 3 - Probar evaluacion offline (sin Telegram)

Ejecuta:

```powershell
python evaluate.py
```

Salida esperada en consola:

`OK -> reports/metrics.json, reports/confusion_matrix.csv, reports/predictions.csv, reports/threshold_analysis.csv`

Si sale ese `OK`, la evaluacion termino correctamente.

## 7) Archivos de salida que debes revisar

Tras ejecutar `evaluate.py`, se crean:

1. `reports/metrics.json`
2. `reports/confusion_matrix.csv`
3. `reports/predictions.csv`
4. `reports/threshold_analysis.csv`

## 8) Explicacion detallada de metricas

Las etiquetas son:
- `0` = benigno
- `1` = phishing/amenaza

### 8.1 Accuracy

Porcentaje total de aciertos.

Formula:

`(TP + TN) / (TP + TN + FP + FN)`

### 8.2 Precision positiva (`precision_pos`)

De los mensajes que el modelo marco como amenaza, cuantos eran realmente amenaza.

Formula:

`TP / (TP + FP)`

Si quieres evitar falsos positivos, esta metrica es clave.

### 8.3 Recall positivo (`recall_pos`)

De todas las amenazas reales, cuantas detecto.

Formula:

`TP / (TP + FN)`

Si quieres evitar amenazas perdidas, esta metrica es clave.

### 8.4 F1 positivo (`f1_pos`)

Balance entre precision y recall.

Formula:

`2 * (precision * recall) / (precision + recall)`

### 8.5 ROC AUC (`roc_auc`)

Mide capacidad de separacion global entre clases usando scores, no solo la etiqueta final.
- Cerca de `1.0` = muy buena separacion.
- Cerca de `0.5` = parecido a azar.

### 8.6 Average Precision (`average_precision`)

Resume la curva precision-recall en un solo valor.
- Mejor cuanto mas cerca de `1.0`.

## 9) Explicacion de la matriz de confusion

Archivo: `reports/confusion_matrix.csv`

Orden de filas/columnas:
- fila real `0`, columna predicha `0` -> TN (verdadero negativo)
- fila real `0`, columna predicha `1` -> FP (falso positivo)
- fila real `1`, columna predicha `0` -> FN (falso negativo)
- fila real `1`, columna predicha `1` -> TP (verdadero positivo)

Ejemplo real de este proyecto en una ejecucion de prueba:

```csv
,0,1
0,41,9
1,9,41
```

Interpretacion:
- 41 benignos bien clasificados.
- 9 benignos marcados por error como amenaza.
- 9 amenazas que se escaparon.
- 41 amenazas detectadas correctamente.

## 10) Explicacion de `predictions.csv`

Cada fila corresponde a un mensaje del dataset:
- `text`: texto original.
- `label`: clase real.
- `pred`: clase predicha.
- `score_1`: probabilidad de clase 1 (amenaza).
- `run_id`: identificador unico de ejecucion.
- `threshold_used`: umbral usado para decidir `pred`.
- `text_sha256`: hash del texto para trazabilidad.

## 11) Explicacion de `threshold_analysis.csv`

Este archivo recalcula metricas para multiples umbrales (0.05 a 0.95).

Sirve para decidir el mejor `THRESHOLD` segun objetivo:
- Si quieres detectar mas amenazas: baja umbral (sube recall, baja precision).
- Si quieres menos alertas falsas: sube umbral (sube precision, baja recall).

## 12) Explicacion de trazabilidad en tiempo real (`main.py` + MongoDB)

Cada mensaje guardado en Mongo incluye:
- identidad de ejecucion: `run_id`
- identidad del mensaje: `chat_id`, `message_id`, `user_id`
- integridad: `msg_sha256`
- resultado de IA: `pred`, `score_1`, `threshold`
- rendimiento: `latency_ms`, `device`
- estado: `ok`, `error`
- tiempo: `created_at_utc`
- origen del modelo: `hf_model`, `model_source`

Esto te permite auditar:
- con que configuracion se predijo,
- en que momento,
- con que score,
- y si hubo error tecnico.

## 13) Ejecutar bot completo con Docker (produccion/demo)

### 13.1 Construir imagen

```powershell
docker compose build
```

### 13.2 Levantar servicios

```powershell
docker compose up
```

Al arrancar por primera vez:
- Te pedira codigo de Telegram por consola.
- Si tienes 2FA, te pedira password.

### 13.3 Ver mensajes guardados en Mongo

En otra terminal:

```powershell
docker exec -it mongo mongosh
```

Dentro de mongosh:

```javascript
use tfg
db.messages.find().sort({created_at_utc:-1}).limit(5).pretty()
```

## 14) Checklist final para decir "funciona"

Debes poder marcar todo esto:

1. `python evaluate.py` termina con `OK -> reports/...`.
2. Existen los 4 archivos en `reports/`.
3. `metrics.json` tiene metricas y metadatos (`run_id`, `model_source`, `input_csv_sha256`).
4. `docker compose up` inicia `mongo` y `bot` sin caidas.
5. Al enviar mensajes de Telegram, aparecen documentos en `db.messages`.

## 15) Errores frecuentes y solucion

### Error: `ModuleNotFoundError`

Solucion:
- activar `.venv`
- reinstalar con `python -m pip install -r requirements.txt`

### Error: modelo spaCy no encontrado (`es_core_news_sm`, etc.)

Solucion:
- ejecutar los 3 comandos `python -m spacy download ...`

### Error: repositorio HF no tiene `pytorch_model.bin`

Solucion:
- ya esta resuelto en el proyecto con `model_loader.py` usando fallback `.pt`.
- asegurese de tener en `.env`:
  - `HF_BASE_MODEL=distilbert-base-uncased`
  - `HF_STATE_DICT_FILE=distilbert_fast_fixed_labels.pt`

### Error: `Falta TELEGRAM_API_ID ...`

Solucion:
- completar `.env` con `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`.

### Error: no descarga de HF o limites

Solucion:
- comprobar internet.
- opcional: exportar token HF para mayor limite (`HF_TOKEN`).

## 16) Recomendacion de configuracion inicial

Para empezar:
- `THRESHOLD=0.05` (prioriza recall en deteccion de amenazas)
- ejecutar evaluacion
- revisar `threshold_analysis.csv`
- ajustar `THRESHOLD` segun prioridad:
  - priorizar deteccion: bajar umbral
  - priorizar menos falsos positivos: subir umbral

## 17) API FastAPI para dashboard y trazabilidad

La API se sirve con:

```powershell
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /api/v1/health`
- `GET /api/v1/runs`
- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/thresholds`
- `GET /api/v1/runs/{run_id}/confusion-matrix`
- `GET /api/v1/messages`
- `GET /api/v1/messages/stats`
- `GET /api/v1/training/metadata`

## 18) Dashboard React + Chart.js

Desde `dashboard-react`:

```powershell
Copy-Item .env.example .env
# editar VITE_API_BASE_URL si aplica
npm install
npm run dev
```

Vistas implementadas:
- Resumen KPI.
- Curva precision/recall/F1 por umbral.
- Matriz de confusion.
- Tabla de mensajes filtrable.
- Trazabilidad de ejecucion y metadata de entrenamiento.

## 19) Grafana MVP

Grafana queda provisionado desde:
- `grafana/provisioning/datasources/datasource.yml`
- `grafana/provisioning/dashboards/dashboard.yml`
- `grafana/dashboards/tfg_mvp_dashboard.json`

Paneles:
- volumen de mensajes,
- proporcion benigno/amenaza,
- latencia media/p95,
- tasa de errores,
- distribucion de `score_1`,
- precision/recall por ejecucion.

## 20) Validacion Fase 5 (integracion + E2E)

Casos simulados:

```powershell
python scripts/simulate_cases.py --write-mongo
```

Runner integral:

```powershell
python scripts/run_phase5_checks.py --write-mongo
```

Artefactos nuevos:
- `reports/simulated_cases_results.csv`
- `reports/e2e_evidence.json`
- `reports/phase5_validation.json`
