from pathlib import Path

from scripts.train_baseline import load_training_config


def test_training_config_resolves_expected_paths() -> None:
    config = load_training_config(Path(__file__).resolve().parents[1] / "configs/training_config.json")

    assert config["dataset_path"].name == "fake_news_unified.csv.gz"
    assert config["reports_dir"].name == "training_runs"
    assert config["candidate_models"][0]["name"] == "logistic_regression"
    assert config["prediction_policy"]["probability_threshold"] == 0.6
    assert config["prediction_policy"]["decision_threshold"] == 0.3
