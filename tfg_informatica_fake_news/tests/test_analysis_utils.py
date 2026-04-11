from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from analysis_utils import (
    build_prediction_examples_payload,
    extract_linear_model_terms_from_pipeline,
    predict_with_threshold_policy,
)


def test_build_prediction_examples_prioritizes_high_absolute_scores() -> None:
    frame = pd.DataFrame(
        [
            {"source_id": "tp-low", "channel": "c1", "date_utc": "", "text": "rumor", "normalized_text": "rumor", "label": 1, "pred": 1, "score": 0.2},
            {"source_id": "tp-high", "channel": "c1", "date_utc": "", "text": "bulo viral", "normalized_text": "bulo viral", "label": 1, "pred": 1, "score": 2.4},
            {"source_id": "tn-only", "channel": "c2", "date_utc": "", "text": "desmentido oficial", "normalized_text": "desmentido oficial", "label": 0, "pred": 0, "score": -1.9},
            {"source_id": "fp-low", "channel": "c3", "date_utc": "", "text": "nota real", "normalized_text": "nota real", "label": 0, "pred": 1, "score": 0.7},
            {"source_id": "fp-high", "channel": "c3", "date_utc": "", "text": "comunicado real", "normalized_text": "comunicado real", "label": 0, "pred": 1, "score": 3.1},
            {"source_id": "fn-only", "channel": "c4", "date_utc": "", "text": "cadena falsa", "normalized_text": "cadena falsa", "label": 1, "pred": 0, "score": -4.0},
        ]
    )

    payload = build_prediction_examples_payload(frame, text_column="normalized_text", top_n=1)

    assert payload["true_positive"][0]["source_id"] == "tp-high"
    assert payload["true_negative"][0]["source_id"] == "tn-only"
    assert payload["false_positive"][0]["source_id"] == "fp-high"
    assert payload["false_negative"][0]["source_id"] == "fn-only"


def test_extract_linear_model_terms_returns_ranked_terms() -> None:
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=300)),
        ]
    )
    texts = pd.Series(
        [
            "bulo falso cadena falsa",
            "rumor falso inventado",
            "desmentido oficial documento verificado",
            "nota oficial verificada",
            "engaño viral falso",
            "comunicado verificado real",
        ]
    )
    labels = pd.Series([1, 1, 0, 0, 1, 0])
    pipeline.fit(texts, labels)

    payload = extract_linear_model_terms_from_pipeline(pipeline, model_name="logistic_regression", top_n=3)

    assert payload is not None
    assert payload["model_name"] == "logistic_regression"
    assert len(payload["positive_class"]["top_terms"]) == 3
    assert len(payload["negative_class"]["top_terms"]) == 3
    positive_terms = {item["term"] for item in payload["positive_class"]["top_terms"]}
    negative_terms = {item["term"] for item in payload["negative_class"]["top_terms"]}
    assert {"falso", "rumor", "engaño"} & positive_terms
    assert {"oficial", "verificado", "real"} & negative_terms


def test_predict_with_threshold_policy_uses_probability_threshold_when_available() -> None:
    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=300)),
        ]
    )
    texts = pd.Series(
        [
            "fraude inventado alarma viral",
            "noticia verificada documento oficial",
            "bulo sin fuente",
            "comunicado oficial contrastado",
            "rumor engañoso compartido",
            "nota real del ministerio",
        ]
    )
    labels = pd.Series([1, 0, 1, 0, 1, 0])
    pipeline.fit(texts, labels)

    predictions, scores, score_kind, threshold_used = predict_with_threshold_policy(
        pipeline,
        texts,
        prediction_policy={"prefer_probability": True, "probability_threshold": 0.9, "decision_threshold": 0.0},
    )

    assert score_kind == "probability"
    assert threshold_used == 0.9
    assert len(predictions) == len(texts)
    assert len(scores) == len(texts)
    assert any(pred == 0 for pred in predictions)
