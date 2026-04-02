from __future__ import annotations

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
