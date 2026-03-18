ESCUELA TECNICA SUPERIOR DE INGENIERIA INFORMATICA

DOBLE GRADO EN INGENIERIA INFORMATICA E INGENIERIA DE COMPUTADORES

CURSO ACADEMICO 2024-2025

TRABAJO FIN DE GRADO

# DETECCION TEMPRANA DE FAKE NEWS EN TELEGRAM MEDIANTE ANALISIS AUTOMATIZADO DE MENSAJES

Autor: Alvaro Osuna Flores

Tutora: Liliana Patricia Santacruz Valencia

## Resumen

Este Trabajo Fin de Grado propone el desarrollo de una base software para detectar de forma temprana noticias falsas difundidas en Telegram. A diferencia del TFG de phishing orientado a sistemas e integracion, este proyecto se centra en el tratamiento de los datos y del lenguaje: extraccion de mensajes, normalizacion textual, tokenizacion, deteccion de idioma y preparacion de una base reutilizable para futuros modelos de clasificacion.

En esta primera fase se implementan los dos primeros objetivos especificos, dejando preparado el terreno para la construccion posterior del dataset, el entrenamiento supervisado y la evaluacion de modelos de fake news.

## 1. Introduccion

### 1.1 Motivacion

Telegram facilita la difusion rapida de contenido y la creacion de comunidades con gran capacidad de replicacion. Ese contexto favorece la propagacion de bulos y fake news, por lo que resulta relevante construir herramientas capaces de recopilar, normalizar y preparar mensajes para su analisis automatizado.

### 1.2 Objetivo general

Desarrollar una base aplicativa orientada al tratamiento de mensajes de Telegram para futuras tareas de deteccion temprana de fake news mediante tecnicas de procesamiento del lenguaje natural.

### 1.3 Objetivos especificos implementados en esta fase

1. Implementar un modulo de extraccion de mensajes desde canales y grupos de Telegram utilizando su API.
2. Disenar un pipeline de preprocesamiento de texto para normalizar los mensajes, incluyendo limpieza, tokenizacion y deteccion de idioma.

## 2. Enfoque diferencial respecto al TFG de Computadores

Este trabajo se diferencia del TFG de phishing en dos planos:

- por tema, al centrarse en fake news en lugar de phishing;
- por enfoque academico, al priorizar datos, logica de procesamiento y preparacion del flujo de analisis frente a arquitectura operativa, despliegue y monitorizacion.

## 3. Arquitectura logica minima

La arquitectura inicial se organiza en tres pasos:

1. `telegram_extractor.py`: adquisicion de mensajes crudos mediante Telethon.
2. `preprocessing.py`: limpieza, normalizacion, tokenizacion y deteccion de idioma.
3. `main.py`: orquestacion del flujo y persistencia de salidas en `data/raw/` y `data/processed/`.

## 4. Herramientas utilizadas

- Python como lenguaje principal.
- Telethon para integracion con Telegram.
- `langdetect` para deteccion automatica de idioma.
- `pytest` para validar extractor y preprocesado.

## 5. Roadmap de siguientes fases

Las siguientes iteraciones deberan abordar:

1. construccion y etiquetado del dataset;
2. entrenamiento y comparativa de modelos de clasificacion;
3. evaluacion con metricas como precision, recall y F1;
4. analisis de resultados y gestion de artefactos.
