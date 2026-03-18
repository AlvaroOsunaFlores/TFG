# TFGs Telegram - Repo Unificado

Este repositorio agrupa dos Trabajos Fin de Grado diferenciados por tema y por enfoque tecnico:

- `tfg_computadores_phishing/`: TFG de Ingenieria de Computadores centrado en sistemas, pipeline, integracion, almacenamiento, monitorizacion y despliegue.
- `tfg_informatica_fake_news/`: TFG de Ingenieria Informatica centrado en tratamiento de datos, preprocesamiento textual, logica de aplicacion y futura fase de entrenamiento y evaluacion.

## Motivo de la separacion

La separacion permite reutilizar la experiencia y parte del camino tecnico del primer proyecto sin mezclar ambos enfoques academicos:

- Computadores prioriza arquitectura operativa extremo a extremo.
- Informatica prioriza el trabajo con datos y el procesamiento de la informacion.

## Estructura del repositorio

```text
proyecto_principal_repo/
|-- tfg_computadores_phishing/
|-- tfg_informatica_fake_news/
|-- .gitignore
`-- README.md
```

## Trabajo recomendado

### TFG de Computadores

```powershell
Set-Location .\tfg_computadores_phishing
Copy-Item .env.example .env
..\.venv\Scripts\python.exe -m pytest -q
```

Si prefieres un entorno virtual propio dentro de la carpeta, puedes crearlo de forma independiente.

### TFG de Informatica

```powershell
Set-Location .\tfg_informatica_fake_news
python main.py --use-sample
python -m pytest -q
```

## Documentacion de referencia

La linea editorial y la estructura academica se alinean con los materiales de `documentacion_referencia` del workspace, especialmente:

- la propuesta breve de fake news en Telegram;
- la propuesta de ciberseguridad en Telegram;
- la memoria larga ETSII usada como patron de estilo y profundidad.

## GitHub

Los cambios de ambos TFG se trabajan en ramas del mismo repositorio remoto para mantener una unica historia y facilitar la entrega.
