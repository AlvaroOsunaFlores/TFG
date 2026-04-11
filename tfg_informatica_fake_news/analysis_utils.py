from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.metrics import confusion_matrix

from scripts.validate_dataset import LABEL_NAMES


DEFAULT_TOP_EXAMPLES = 5
DEFAULT_TOP_TERMS = 15
DEFAULT_PREDICTION_POLICY = {
    "prefer_probability": True,
    "probability_threshold": 0.6,
    "decision_threshold": 0.3,
}


def _round_float(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def _summarize_numeric(values: list[int]) -> dict[str, float | int]:
    series = pd.Series(values, dtype="float64")
    return {
        "mean": _round_float(series.mean(), digits=2),
        "median": _round_float(series.median(), digits=2),
        "min": int(series.min()),
        "max": int(series.max()),
    }


def build_dataset_summary(df: pd.DataFrame) -> dict[str, Any]:
    raw_char_count = df["text"].astype(str).map(len).tolist()
    normalized_token_count = df["normalized_text"].astype(str).map(lambda value: len(value.split())).tolist()
    language_distribution = {
        str(key): int(value)
        for key, value in df["language"].astype(str).value_counts().sort_index().items()
    }
    return {
        "rows": int(len(df)),
        "label_distribution": {
            str(key): int(value)
            for key, value in df["label"].value_counts().sort_index().items()
        },
        "language_distribution": language_distribution,
        "included_languages": sorted(language_distribution.keys()),
        "text_length_summary": {
            "raw_char_count": _summarize_numeric(raw_char_count),
            "normalized_token_count": _summarize_numeric(normalized_token_count),
        },
    }


def resolve_prediction_policy(config_policy: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = dict(DEFAULT_PREDICTION_POLICY)
    if config_policy:
        policy.update(config_policy)
    policy["prefer_probability"] = bool(policy.get("prefer_probability", True))
    policy["probability_threshold"] = float(policy.get("probability_threshold", 0.5))
    policy["decision_threshold"] = float(policy.get("decision_threshold", 0.0))
    return policy


def predict_with_threshold_policy(
    model: Any,
    texts: pd.Series,
    *,
    prediction_policy: dict[str, Any] | None = None,
) -> tuple[list[int], list[float | None], str, float | None]:
    policy = resolve_prediction_policy(prediction_policy)
    texts = texts.astype(str)

    if policy["prefer_probability"] and hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(texts)
        scores = probabilities[:, -1].tolist()
        threshold_used = float(policy["probability_threshold"])
        predictions = [1 if float(score) >= threshold_used else 0 for score in scores]
        return predictions, [float(score) for score in scores], "probability", threshold_used

    if hasattr(model, "decision_function"):
        raw_scores = model.decision_function(texts)
        if hasattr(raw_scores, "tolist"):
            raw_scores = raw_scores.tolist()
        scores = [float(value) for value in raw_scores]
        threshold_used = float(policy["decision_threshold"])
        predictions = [1 if float(score) >= threshold_used else 0 for score in scores]
        return predictions, scores, "decision_function", threshold_used

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(texts)
        scores = probabilities[:, -1].tolist()
        threshold_used = float(policy["probability_threshold"])
        predictions = [1 if float(score) >= threshold_used else 0 for score in scores]
        return predictions, [float(score) for score in scores], "probability", threshold_used

    predictions = [int(value) for value in model.predict(texts)]
    return predictions, [None] * len(predictions), "predict", None


def extract_prediction_scores(model: Any, texts: pd.Series) -> list[float | None]:
    try:
        _predictions, scores, _score_kind, _threshold_used = predict_with_threshold_policy(
            model,
            texts,
            prediction_policy=DEFAULT_PREDICTION_POLICY,
        )
        return scores
    except Exception:
        return [None] * len(texts)


def build_confusion_matrix_payload(y_true: pd.Series, y_pred: pd.Series) -> dict[str, Any]:
    matrix = confusion_matrix(y_true.astype(int), y_pred.astype(int), labels=[0, 1])
    return {
        "labels": [
            {"label": 0, "label_name": LABEL_NAMES[0]},
            {"label": 1, "label_name": LABEL_NAMES[1]},
        ],
        "matrix": matrix.tolist(),
        "by_actual": {
            LABEL_NAMES[0]: {
                LABEL_NAMES[0]: int(matrix[0][0]),
                LABEL_NAMES[1]: int(matrix[0][1]),
            },
            LABEL_NAMES[1]: {
                LABEL_NAMES[0]: int(matrix[1][0]),
                LABEL_NAMES[1]: int(matrix[1][1]),
            },
        },
    }


def build_prediction_examples_payload(
    frame: pd.DataFrame,
    *,
    text_column: str,
    top_n: int = DEFAULT_TOP_EXAMPLES,
) -> dict[str, list[dict[str, Any]]]:
    working = frame.copy()
    if "score" not in working.columns:
        working["score"] = None

    working["score"] = pd.to_numeric(working["score"], errors="coerce")
    working["abs_score"] = working["score"].abs()

    buckets = {
        "true_positive": (working["label"] == 1) & (working["pred"] == 1),
        "true_negative": (working["label"] == 0) & (working["pred"] == 0),
        "false_positive": (working["label"] == 0) & (working["pred"] == 1),
        "false_negative": (working["label"] == 1) & (working["pred"] == 0),
    }

    payload: dict[str, list[dict[str, Any]]] = {}
    for bucket_name, mask in buckets.items():
        subset = working.loc[mask].copy()
        if subset.empty:
            payload[bucket_name] = []
            continue

        if subset["score"].notna().any():
            subset = subset.sort_values(["abs_score", "source_id"], ascending=[False, True])
        else:
            subset = subset.sort_values("source_id")

        records: list[dict[str, Any]] = []
        for row in subset.head(top_n).itertuples(index=False):
            records.append(
                {
                    "source_id": getattr(row, "source_id", ""),
                    "channel": getattr(row, "channel", ""),
                    "date_utc": getattr(row, "date_utc", ""),
                    "text": getattr(row, "text", ""),
                    "normalized_text": getattr(row, "normalized_text", ""),
                    "analysis_text": getattr(row, text_column, ""),
                    "true_label": int(getattr(row, "label")),
                    "true_label_name": LABEL_NAMES[int(getattr(row, "label"))],
                    "predicted_label": int(getattr(row, "pred")),
                    "predicted_label_name": LABEL_NAMES[int(getattr(row, "pred"))],
                    "score": None if pd.isna(getattr(row, "score")) else _round_float(getattr(row, "score"), digits=6),
                }
            )
        payload[bucket_name] = records

    return payload


def extract_linear_model_terms_from_pipeline(
    pipeline: Any,
    *,
    model_name: str,
    top_n: int = DEFAULT_TOP_TERMS,
) -> dict[str, Any] | None:
    named_steps = getattr(pipeline, "named_steps", {})
    vectorizer = named_steps.get("tfidf")
    classifier = named_steps.get("classifier")
    if vectorizer is None or classifier is None or not hasattr(classifier, "coef_"):
        return None

    coefficients = classifier.coef_
    if getattr(coefficients, "ndim", 1) != 2 or coefficients.shape[0] == 0:
        return None

    feature_names = vectorizer.get_feature_names_out()
    weights = coefficients[0]

    ranked = sorted(
        (
            {"term": str(term), "weight": _round_float(weight, digits=6)}
            for term, weight in zip(feature_names, weights, strict=False)
        ),
        key=lambda item: item["weight"],
    )
    negative_terms = ranked[:top_n]
    positive_terms = list(reversed(ranked[-top_n:]))

    return {
        "model_name": model_name,
        "feature_count": int(len(feature_names)),
        "negative_class": {
            "label": 0,
            "label_name": LABEL_NAMES[0],
            "top_terms": negative_terms,
        },
        "positive_class": {
            "label": 1,
            "label_name": LABEL_NAMES[1],
            "top_terms": positive_terms,
        },
    }
