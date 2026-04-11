from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_dataset(path: Path) -> None:
    frame = pd.DataFrame(
        [
            {
                "source_id": f"id-{index}",
                "channel": "canal",
                "date_utc": "2026-04-02T18:00:00+00:00",
                "text": text,
                "normalized_text": text,
                "language": "es",
                "label": label,
                "label_name": "fake_news" if label == 1 else "verificado_o_neutro",
                "source": "test",
            }
            for index, (text, label) in enumerate(
                [
                    ("rumor falso sobre vacunas", 1),
                    ("desmentido oficial del rumor", 0),
                    ("bulo viral sin fuente", 1),
                    ("comunicado verificado del ministerio", 0),
                    ("cadena alarmista inventada", 1),
                    ("nota contrastada por fact-checkers", 0),
                    ("manipulacion de titular en telegram", 1),
                    ("aclaracion publicada por organismo oficial", 0),
                ],
                start=1,
            )
        ]
    )
    frame.to_csv(path, index=False)


def test_train_baseline_creates_manifest(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.csv"
    reports_dir = tmp_path / "reports"
    models_dir = tmp_path / "models"
    config_path = tmp_path / "training_config.json"
    _write_dataset(dataset_path)

    config_path.write_text(
        json.dumps(
            {
                "dataset_path": str(dataset_path),
                "text_column": "normalized_text",
                "label_column": "label",
                "test_size": 0.25,
                "random_state": 42,
                "selection_metric": "macro_f1",
                "reports_dir": str(reports_dir),
                "model_output_dir": str(models_dir),
                "candidate_models": [
                    {
                        "name": "logistic_regression",
                        "classifier": "logistic_regression",
                        "tfidf": {"ngram_range": [1, 2], "min_df": 1, "max_features": 100},
                        "params": {"C": 1.0, "max_iter": 200, "class_weight": "balanced"},
                    }
                ],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "scripts.train_baseline", "--config", str(config_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    manifests = list(reports_dir.glob("baseline-*/training_manifest.json"))
    assert manifests, result.stdout
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert manifest["dataset_summary"]["rows"] == 8
    assert manifest["prediction_policy"]["probability_threshold"] == 0.6
    assert manifest["prediction_policy"]["decision_threshold"] == 0.3
    assert manifest["best_model_score_kind"] in {"probability", "decision_function", "predict"}
    assert Path(manifest["confusion_matrix_path"]).exists()
    assert Path(manifest["prediction_examples_path"]).exists()
    assert Path(manifest["linear_model_terms_path"]).exists()

    run_dir = manifests[0].parent
    assert (run_dir / "holdout_predictions.csv").exists()
    assert (run_dir / "confusion_matrix.json").exists()
    assert (run_dir / "prediction_examples.json").exists()
    assert (run_dir / "linear_model_terms.json").exists()
