from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


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
                ],
                start=1,
            )
        ]
    )
    frame.to_csv(path, index=False)


def test_evaluate_baseline_generates_summary(tmp_path: Path) -> None:
    dataset_path = tmp_path / "dataset.csv"
    model_path = tmp_path / "baseline_pipeline.joblib"
    outdir = tmp_path / "evaluations"
    _write_dataset(dataset_path)

    frame = pd.read_csv(dataset_path)
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=200)),
        ]
    )
    model.fit(frame["normalized_text"], frame["label"])
    joblib.dump(model, model_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.evaluate_baseline",
            "--dataset",
            str(dataset_path),
            "--model",
            str(model_path),
            "--outdir",
            str(outdir),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    summaries = list(outdir.glob("evaluation-*/evaluation_summary_*.json"))
    assert summaries, result.stdout
    summary = json.loads(summaries[0].read_text(encoding="utf-8"))
    assert summary["dataset_summary"]["rows"] == 4
    assert summary["prediction_policy"]["probability_threshold"] == 0.6
    assert summary["prediction_policy"]["decision_threshold"] == 0.3
    assert summary["score_kind"] in {"probability", "decision_function", "predict"}
    assert Path(summary["confusion_matrix_path"]).exists()
    assert Path(summary["prediction_examples_path"]).exists()
    assert Path(summary["linear_model_terms_path"]).exists()

    run_dir = summaries[0].parent
    assert len(list(run_dir.glob("evaluation_predictions_*.csv"))) == 1
    assert (run_dir / "confusion_matrix.json").exists()
    assert (run_dir / "prediction_examples.json").exists()
    assert (run_dir / "linear_model_terms.json").exists()
