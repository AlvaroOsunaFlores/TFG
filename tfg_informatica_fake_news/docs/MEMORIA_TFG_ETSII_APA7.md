ESCUELA TECNICA SUPERIOR DE INGENIERIA INFORMATICA

DOBLE GRADO EN INGENIERIA INFORMATICA E INGENIERIA DE COMPUTADORES

CURSO ACADEMICO 2024-2025

TRABAJO FIN DE GRADO

# DETECCION TEMPRANA DE FAKE NEWS EN TELEGRAM MEDIANTE ANALISIS AUTOMATIZADO DE MENSAJES

Autor: Alvaro Osuna Flores

Tutora: Liliana Patricia Santacruz Valencia

## Resumen

Este documento recoge la base inicial del TFG de Ingenieria Informatica dedicado a la deteccion temprana de fake news en Telegram. En esta fase se implementan la extraccion de mensajes mediante la API de Telegram y el pipeline de preprocesamiento encargado de limpiar, tokenizar y detectar el idioma de cada mensaje.

## 1. Introduccion

Telegram facilita la difusion masiva y veloz de contenidos, incluidos bulos y noticias falsas. Por ello resulta conveniente construir una base software que permita recopilar mensajes, normalizarlos y prepararlos para futuras tareas de entrenamiento y evaluacion de modelos de clasificacion.

## 2. Objetivo general

Desarrollar una base de tratamiento de mensajes de Telegram orientada a la deteccion de fake news, poniendo el foco en datos, preprocesamiento y logica de aplicacion.

## 3. Objetivos especificos implementados

1. Implementar un modulo de extraccion de mensajes desde canales y grupos de Telegram utilizando su API.
2. Disenar un pipeline de preprocesamiento de texto para normalizar los mensajes, incluyendo limpieza, tokenizacion y deteccion de idioma.

## 4. Arquitectura minima

El proyecto se organiza en tres modulos:

- `telegram_extractor.py` para obtener mensajes crudos.
- `preprocessing.py` para normalizar el contenido textual.
- `main.py` para orquestar el flujo y generar salidas en `data/raw/` y `data/processed/`.

## 5. Siguientes pasos

Las siguientes iteraciones deberan ampliar el proyecto con:

1. construccion de dataset etiquetado;
2. entrenamiento y comparativa de modelos;
3. evaluacion con metricas y analisis de errores;
4. gestion de resultados y memoria completa.
