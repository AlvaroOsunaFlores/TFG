ESCUELA TECNICA SUPERIOR DE INGENIERIA INFORMATICA

DOBLE GRADO EN INGENIERIA INFORMATICA E INGENIERIA DE COMPUTADORES

CURSO ACADEMICO 2024-2025

TRABAJO FIN DE GRADO

# DETECCION TEMPRANA DE FAKE NEWS EN TELEGRAM MEDIANTE ANALISIS AUTOMATIZADO DE MENSAJES

Autor: Alvaro Osuna Flores

Tutora: Liliana Patricia Santacruz Valencia

## Resumen

Este documento recoge el estado actual del TFG de Ingenieria Informatica dedicado a la deteccion temprana de fake news en Telegram. En esta fase se implementan la extraccion de mensajes mediante la API de Telegram, el pipeline de preprocesamiento encargado de limpiar, tokenizar y detectar el idioma de cada mensaje, y la preparacion de la siguiente etapa mediante un dataset ficticio etiquetado y scripts reproducibles para entrenamiento y evaluacion futura.

## 1. Introduccion

Telegram facilita la difusion masiva y veloz de contenidos, incluidos bulos y noticias falsas. Por ello resulta conveniente construir una base software que permita recopilar mensajes, normalizarlos y prepararlos para futuras tareas de entrenamiento y evaluacion de modelos de clasificacion.

## 2. Objetivo general

Desarrollar una base de tratamiento de mensajes de Telegram orientada a la deteccion de fake news, poniendo el foco en datos, preprocesamiento y logica de aplicacion.

## 3. Objetivos especificos implementados

1. Implementar un modulo de extraccion de mensajes desde canales y grupos de Telegram utilizando su API.
2. Disenar un pipeline de preprocesamiento de texto para normalizar los mensajes, incluyendo limpieza, tokenizacion y deteccion de idioma.
3. Construir un dataset ficticio etiquetado con una schema estable que sirva como base tecnica para la siguiente fase del proyecto.
4. Dejar preparados los scripts y la configuracion necesarios para entrenar y evaluar modelos mas adelante, sin ejecutar todavia entrenamiento real.

## 4. Arquitectura minima

El proyecto se organiza en cuatro bloques:

- `telegram_extractor.py` para obtener mensajes crudos.
- `preprocessing.py` para normalizar el contenido textual.
- `main.py` para orquestar el flujo y generar salidas en `data/raw/` y `data/processed/`.
- `scripts/` y `configs/training_config.json` para preparar dataset etiquetado, validacion, entrenamiento baseline y evaluacion posterior.

La preparacion de la fase siguiente se apoya ademas en `data/labeled/fake_news_seed.csv`, que actua como dataset semilla ficticio. Su unica finalidad es comprobar estructura, etiquetas, rutas y comandos antes de sustituirlo por un dataset real. En consecuencia, la memoria no presenta aun resultados de entrenamiento ni metricas de IA obtenidas sobre un conjunto academico definitivo.

## 5. Siguientes pasos

Las siguientes iteraciones deberan ampliar el proyecto con:

1. sustitucion del dataset ficticio por un dataset real y validado;
2. entrenamiento y comparativa de modelos sobre datos reales;
3. evaluacion con metricas y analisis de errores apoyados en artefactos persistidos;
4. ampliacion de la memoria con resultados experimentales finales.
