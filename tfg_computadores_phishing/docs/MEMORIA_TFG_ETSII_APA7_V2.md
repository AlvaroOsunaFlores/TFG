ESCUELA TECNICA SUPERIOR DE INGENIERIA INFORMATICA

DOBLE GRADO EN INGENIERIA INFORMATICA E INGENIERIA DE COMPUTADORES

CURSO ACADEMICO 2024-2025

TRABAJO FIN DE GRADO

# TELEGRAM COMO FUENTE DE INTELIGENCIA EN CIBERSEGURIDAD: PROCESAMIENTO DE MENSAJES MEDIANTE IA PARA LA PROTECCION DE EMPRESAS

Autor: Alvaro Osuna Flores

Tutora: Liliana Patricia Santacruz Valencia

## Resumen

Este Trabajo Fin de Grado presenta una solucion para clasificar mensajes de Telegram relevantes para ciberseguridad en un contexto empresarial. La propuesta integra ingesta de mensajes, inferencia mediante un modelo transformer previamente entrenado, persistencia de evidencia tecnica en MongoDB, evaluacion offline reproducible y exposicion de resultados por medio de una API y de paneles de visualizacion.

Tras la revision de tutoria, el nucleo del trabajo se ha reforzado en tres aspectos: seguridad minima del sistema, minimizacion de datos y coherencia entre artefactos tecnicos y explotacion por `run_id`. El objetivo ya no es solo demostrar que el MVP funciona, sino que la solucion queda tecnicamente defendible para memoria y presentacion.

La politica operativa mantiene `THRESHOLD=0.05`, priorizando recall alto en deteccion temprana. Esta eleccion se justifica con el analisis por umbral incluido en los artefactos de evaluacion, que permite comparar el comportamiento de precision, recall y F1 ante distintos puntos de corte.

Palabras clave: Telegram, ciberseguridad, NLP, DistilBERT, FastAPI, trazabilidad, privacidad.

## 1. Introduccion

### 1.1 Motivacion

La comunicacion digital en entornos empresariales se ha convertido en un vector relevante tanto para la colaboracion diaria como para la difusion de campañas de phishing, fraude y robo de credenciales. Telegram resulta especialmente interesante por su rapidez, su estructura de canales y grupos y su capacidad para difundir informacion en tiempo real.

El analisis manual de mensajes presenta problemas de coste, escalabilidad y consistencia. Ademas, si no existe una evidencia tecnica bien definida, resulta dificil justificar por que un mensaje fue marcado como benigno o como amenaza. Por ello, el trabajo propone automatizar la primera clasificacion y dejar una traza tecnica suficiente para auditoria posterior.

### 1.2 Objetivos

Los objetivos principales del trabajo son los siguientes:

1. Diseñar un pipeline completo para clasificar mensajes de Telegram relacionados con ciberseguridad.
2. Mantener trazabilidad tecnica suficiente para explicar la decision tomada por el modelo.
3. Publicar resultados por medio de una API reutilizable.
4. Visualizar ejecuciones, metricas y mensajes desde un dashboard y desde Grafana.
5. Reducir exposicion innecesaria de datos sensibles para que el sistema sea defendible en memoria y tutoria.

### 1.3 Estructura del documento

La memoria se organiza en introduccion, contexto, descripcion informatica, solucion aplicada, evaluacion de resultados y conclusiones.

## 2. Contexto

### 2.1 Telegram como fuente de inteligencia

Telegram permite mensajes directos, grupos y canales con una elevada velocidad de propagacion del contenido. Esa combinacion lo convierte en una fuente util para obtener señales tempranas de amenazas, pero tambien en un medio propicio para campañas maliciosas.

### 2.2 Necesidad de automatizacion y evidencia

La automatizacion apoyada en modelos de lenguaje reduce el volumen de revision manual y permite homogeneizar la primera clasificacion. Sin embargo, en un entorno academico y tecnico no basta con devolver un `0` o un `1`: hace falta justificar la salida con evidencia reproducible.

### 2.3 Criterio de seguridad minima

Tras la revision de tutoria se adopta un criterio de seguridad minima. Esto implica:

- no exponer MongoDB al exterior por defecto;
- no dejar la API abierta;
- no mantener Grafana con acceso anonimo;
- no almacenar mas datos sensibles de los estrictamente necesarios;
- limitar la retencion de evidencias operativas.

## 3. Descripcion informatica

### 3.1 Arquitectura general

La solucion se estructura en los siguientes componentes:

- `main.py`: ingesta, inferencia y persistencia.
- `evaluate.py`: evaluacion offline reproducible.
- `api/`: publicacion de resultados por FastAPI.
- `dashboard-react/`: visualizacion web.
- `grafana/`: panelizacion complementaria.
- `scripts/simulate_cases.py` y `scripts/run_phase5_checks.py`: validacion extremo a extremo.

### 3.2 Requisitos funcionales

| Requisito | Descripcion |
| --- | --- |
| RF-1 | Clasificar cada mensaje como benigno o amenaza. |
| RF-2 | Guardar evidencia tecnica minima para auditoria. |
| RF-3 | Versionar artefactos por `run_id`. |
| RF-4 | Exponer resultados mediante API. |
| RF-5 | Visualizar resultados en React y Grafana. |

### 3.3 Requisitos no funcionales

| Requisito | Descripcion |
| --- | --- |
| RNF-1 | Reproducibilidad de la evaluacion. |
| RNF-2 | Trazabilidad por hash y contexto de ejecucion. |
| RNF-3 | Minimizacion de datos por defecto. |
| RNF-4 | Mantenibilidad modular. |

## 4. Solucion aplicada

### 4.1 Modelo y politica de decision

El modelo de clasificacion binaria fue entrenado previamente con `AITrainer_distilbert_2.py` a partir de `distilbert-base-uncased`. La explotacion operativa mantiene `THRESHOLD=0.05`.

La justificacion de este valor es funcional: el sistema se orienta a deteccion preventiva. En ese escenario suele ser preferible revisar falsos positivos antes que dejar pasar amenazas reales. Por ello se prioriza recall alto, sin ocultar el coste asociado en precision.

### 4.2 Trazabilidad minima y privacidad

La traza almacenada por defecto en MongoDB incluye:

- `run_id`;
- `created_at_utc`;
- `message_id`;
- `user_hash` y `chat_hash`;
- `msg_sha256`;
- `pred`, `score_1`, `latency_ms`;
- `threshold`, `hf_model`, `model_source`, `device`;
- `ok` y `error`.

Se desactiva por defecto el almacenamiento de:

- `msg_original`;
- `msg_limpio`;
- `tokens`.

Esta decision permite mantener identificacion tecnica e integridad del contenido sin exponer innecesariamente texto sensible o datos personales directos. Ademas, se aplica retencion limitada mediante TTL en MongoDB.

### 4.3 Artefactos por ejecucion

Uno de los cambios mas importantes consiste en dejar de tratar todos los CSV y JSON como si fueran un unico estado global. A partir de esta revision, los artefactos de evaluacion se organizan en `reports/runs/<run_id>/`.

De este modo, los endpoints:

- `GET /api/v1/runs/{run_id}/summary`
- `GET /api/v1/runs/{run_id}/thresholds`
- `GET /api/v1/runs/{run_id}/confusion-matrix`

consultan los ficheros que corresponden realmente a ese `run_id`. La raiz de `reports/` conserva solo una copia del ultimo resultado como acceso rapido y compatibilidad operativa.

### 4.4 Hardening de la explotacion

Se aplican las siguientes medidas:

- FastAPI exige `X-API-Key` en todos los endpoints.
- CORS queda restringido a origenes locales explicitos.
- Grafana deja de aceptar acceso anonimo.
- MongoDB no publica puerto al exterior en Docker.
- El dashboard React incorpora la clave de API por configuracion de entorno.

Estas medidas no convierten el MVP en una plataforma final de produccion, pero corrigen las exposiciones evidentes que hacian el sistema menos defendible.

## 5. Evaluacion de resultados

### 5.1 Metricas principales

La evaluacion offline genera `metrics.json`, `predictions.csv`, `threshold_analysis.csv` y `confusion_matrix.csv`. Las metricas principales utilizadas son:

- accuracy;
- precision de la clase positiva;
- recall de la clase positiva;
- F1;
- ROC AUC;
- average precision.

### 5.2 Justificacion de las metricas elegidas

No se utiliza una unica metrica porque cada una responde a una pregunta distinta:

- accuracy indica el porcentaje total de aciertos;
- precision indica cuanto del ruido generado como amenaza era realmente amenaza;
- recall indica cuantas amenazas reales se detectaron;
- F1 resume el equilibrio entre precision y recall.

En este trabajo, recall tiene un peso especial por el objetivo preventivo del sistema. Aun asi, el analisis por umbral se mantiene precisamente para no esconder el coste operativo de esa decision.

### 5.3 Integracion y validacion

Los scripts de Fase 5 generan evidencia de integracion con casos simulados y consolidan el estado en `phase5_validation.json`. Esta validacion no pretende sustituir pruebas a gran escala, pero si demostrar coherencia entre:

- inferencia,
- persistencia,
- reportes,
- API,
- dashboard,
- y Grafana.

## 6. Conclusiones

La solucion desarrollada cumple los objetivos funcionales del MVP y, tras la revision de tutoria, mejora de forma clara en coherencia tecnica. Los cambios mas relevantes no han sido esteticos, sino estructurales: se ha reforzado seguridad minima, se ha reducido la exposicion de datos y se ha corregido la relacion entre `run_id` y artefactos versionados.

En consecuencia, el proyecto queda mejor preparado para memoria y defensa. La Raspberry Pi se mantiene como linea de trabajo futura razonable, pero no como prioridad inmediata. En el estado actual resulta mas importante consolidar un nucleo tecnico defendible que ampliar el despliegue.
