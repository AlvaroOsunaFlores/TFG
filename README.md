# TFGs Telegram - Repo Unificado

Este repositorio agrupa dos Trabajos Fin de Grado que comparten el contexto Telegram, pero estan diferenciados de forma explicita por alcance tecnico, valor academico y criterio de evaluacion.

- `tfg_computadores_phishing/`: TFG de Ingenieria de Computadores centrado en arquitectura de sistemas, integracion de componentes, observabilidad, persistencia y despliegue del pipeline.
- `tfg_informatica_fake_news/`: TFG de Ingenieria Informatica centrado en extraccion de datos, preprocessing, deduplicacion, construccion de dataset, entrenamiento y evaluacion reproducible.

## Criterio de separacion

La separacion no se apoya solo en el tema, sino en el tipo de problema tecnico que resuelve cada trabajo:

- Computadores estudia como desacoplar ingesta, cola, inferencia, almacenamiento, API y monitorizacion para construir un sistema operable.
- Informatica estudia como organizar el flujo de datos, la calidad del texto, la trazabilidad del dataset y la experimentacion sobre modelos.

## Estructura

```text
proyecto_principal_repo/
|-- tfg_computadores_phishing/
|-- tfg_informatica_fake_news/
|-- .github/workflows/ci.yml
`-- README.md
```

## TFG de Computadores

Arquitectura actual:

`producer -> RabbitMQ -> worker -> MongoDB -> FastAPI -> React`

Observabilidad:

`worker/api -> Prometheus -> Grafana`

Incluye:

- latencias por etapa (`preprocess`, `inference`, `db_write`, `queue_wait`, `end_to_end`);
- metricas de recursos con `psutil`;
- benchmark controlado para `1`, `5`, `10` y `20` mensajes por segundo;
- artefactos de evaluacion y benchmark versionados;
- dashboard React y paneles Grafana sobre Prometheus.

Entrada recomendada:

- `tfg_computadores_phishing/README.md`
- `tfg_computadores_phishing/docs/API_CONTRACT.md`
- `tfg_computadores_phishing/docs/MEMORIA_TFG_GIC_Alvaro_Osuna_Flores.docx`

Validacion minima:

```powershell
Set-Location .\tfg_computadores_phishing
python -m pip install -r requirements.txt
python -m pytest -q
python -m scripts.benchmark_pipeline --duration-seconds 5 --rates 1 5 10 20
```

## TFG de Informatica

Pipeline actual:

`archive2 + LIAR -> corpus auditado -> cinco folds agrupados -> TF-IDF + modelos lineales -> evaluacion y transferencia`

Telegram es un modulo complementario independiente; sus mensajes no participan en el entrenamiento ni en la evaluacion de este TFG.

Incluye:

- corpus canonico y derivado, auditoria de duplicados y particiones por grupo;
- regresion logistica y Linear SVC, con transferencia entre fuentes en ambas direcciones;
- predicciones, metricas, modelos comprimidos y hashes del experimento documentado;
- dependencias fijadas, restauracion verificable y guia de reproduccion;
- pruebas de componentes y CI en GitHub Actions.

Entrada recomendada:

- `tfg_informatica_fake_news/README.md`
- `tfg_informatica_fake_news/docs/REPRODUCIBILIDAD.md`
- `tfg_informatica_fake_news/scripts/run_robustness_experiments.py`
- `tfg_informatica_fake_news/reports/robustness_runs/robustness-1a94400d502b149f/robustness_manifest.json`

Validacion minima:

```powershell
Set-Location .\tfg_informatica_fake_news
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-reproducible.txt
.\.venv\Scripts\python.exe -m scripts.restore_artifacts
.\.venv\Scripts\python.exe -m scripts.verify_reproducibility --check-results
.\.venv\Scripts\python.exe -m scripts.run_robustness_experiments --config configs/robustness_reproduction.json --dry-run
.\.venv\Scripts\python.exe -m pytest -q
```

## Entrega

La carpeta `proyectos_principales/entrega_YYYY_MM_DD` se genera como exportacion limpia para revision, manteniendo ambos TFGs separados pero coherentes dentro de una misma entrega.
