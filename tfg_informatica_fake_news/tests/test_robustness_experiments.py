from __future__ import annotations

import pandas as pd

from scripts.run_robustness_experiments import (
    connected_components,
    lsh_candidates,
    metric_payload,
    minhash_signature,
    prepare_derived_dataset,
    text_shingles,
)


def _config() -> dict:
    return {
        "text_column": "normalized_text", "label_column": "label", "shingle_size": 5,
        "minhash_permutations": 128, "lsh_bands": 32, "signature_batch_size": 1, "random_state": 42,
        "near_duplicate_jaccard": 0.9,
    }


def _frame(rows: list[tuple[str, str, int, str]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["source_id", "normalized_text", "label", "dataset_name"])


def test_short_texts_only_match_exactly() -> None:
    assert text_shingles("one two", 5) != text_shingles("one three", 5)
    assert text_shingles("one two", 5) == text_shingles("one two", 5)


def test_minhash_uses_all_shingles_and_is_deterministic() -> None:
    import numpy as np
    prime = np.uint64(4_294_967_291)
    rng = np.random.default_rng(42)
    a = rng.integers(1, int(prime) - 1, size=128, dtype=np.uint64)
    b = rng.integers(0, int(prime) - 1, size=128, dtype=np.uint64)
    base = {i * 1009 for i in range(600)}
    changed_only_at_end = set(base)
    changed_only_at_end.difference_update({i * 1009 for i in range(500, 600)})
    changed_only_at_end.update({1_000_000 + i for i in range(100)})
    first = minhash_signature(base, a, b)
    assert first == minhash_signature(base, a, b)
    assert len(first) == 128
    assert first != minhash_signature(changed_only_at_end, a, b)


def test_lsh_groups_candidates_sharing_a_band() -> None:
    signature = tuple(range(128))
    almost_same = tuple([*range(124), 1000, 1001, 1002, 1003])
    assert (0, 1) in lsh_candidates([signature, almost_same], 32)


def test_exact_duplicates_keep_smallest_source_id_and_audit_alias() -> None:
    derived, audit, metadata = prepare_derived_dataset(
        _frame([("z", "one two three four five six", 0, "archive2_news_dataset"), ("a", "one two three four five six", 0, "archive2_news_dataset")]), _config()
    )
    assert derived["source_id"].tolist() == ["a"]
    assert set(audit["source_id"]) == {"a", "z"}
    assert metadata["exact_duplicate_rows_collapsed"] == 1


def test_exact_conflicting_labels_exclude_whole_group_and_retain_audit() -> None:
    derived, audit, metadata = prepare_derived_dataset(
        _frame([("a", "one two three four five six", 0, "archive2_news_dataset"), ("b", "one two three four five six", 1, "liar_politifact")]), _config()
    )
    assert derived.empty
    assert metadata["exact_conflicting_groups_excluded"] == 1
    assert metadata["exact_conflicting_rows_excluded"] == 2
    assert set(audit["status"]) == {"excluded_conflicting_duplicate_group"}


def test_exact_conflict_propagates_to_near_duplicate_component() -> None:
    shared = " ".join(f"token{i}" for i in range(5, 205))
    base = "alpha beta gamma delta epsilon " + shared
    near = "alpha beta gamma delta omega " + shared
    derived, audit, metadata = prepare_derived_dataset(
        _frame([("a", base, 0, "archive2_news_dataset"), ("b", base, 1, "liar_politifact"), ("c", near, 0, "archive2_news_dataset")]), _config()
    )
    assert derived.empty
    assert set(audit["source_id"]) == {"a", "b", "c"}
    assert set(audit["status"]) == {"excluded_conflicting_duplicate_group"}
    assert metadata["conflicting_rows_excluded"] == 3


def test_new_derived_label_names_negative_class_no_fake() -> None:
    derived, _audit, _metadata = prepare_derived_dataset(
        _frame([("a", "alpha bravo charlie delta echo foxtrot", 0, "archive2_news_dataset"), ("b", "lima mike november oscar papa quebec", 1, "liar_politifact")]), _config()
    )
    assert dict(zip(derived["label"], derived["label_name"])) == {0: "no_fake", 1: "fake_news"}


def test_near_duplicate_variants_remain_together_in_group() -> None:
    shared = " ".join(f"token{i}" for i in range(5, 205))
    left = "alpha beta gamma delta epsilon " + shared
    right = "alpha beta gamma delta omega " + shared
    derived, _audit, _metadata = prepare_derived_dataset(
        _frame([("a", left, 0, "archive2_news_dataset"), ("b", right, 0, "archive2_news_dataset")]), _config()
    )
    assert set(derived["source_id"]) == {"a", "b"}
    assert derived["duplicate_group"].nunique() == 1


def test_conflicting_near_duplicate_group_excludes_every_member() -> None:
    shared = " ".join(f"token{i}" for i in range(5, 205))
    left = "alpha beta gamma delta epsilon " + shared
    right = "alpha beta gamma delta omega " + shared
    derived, audit, metadata = prepare_derived_dataset(
        _frame([("a", left, 0, "archive2_news_dataset"), ("b", right, 1, "liar_politifact")]), _config()
    )
    assert derived.empty
    assert metadata["conflicting_groups_excluded"] == 1
    assert set(audit["status"]) == {"excluded_conflicting_duplicate_group"}


def test_cross_source_provenance_is_combined_on_group() -> None:
    shared = " ".join(f"token{i}" for i in range(5, 205))
    left = "alpha beta gamma delta epsilon " + shared
    right = "alpha beta gamma delta omega " + shared
    derived, _audit, metadata = prepare_derived_dataset(
        _frame([("a", left, 0, "archive2_news_dataset"), ("b", right, 0, "liar_politifact")]), _config()
    )
    assert derived["is_cross_source_group"].all()
    assert metadata["cross_source_groups"] == 1


def test_connected_components_are_transitive() -> None:
    groups = connected_components(5, [(0, 1), (1, 2), (3, 4)])
    assert groups[0] == groups[1] == groups[2]
    assert groups[3] == groups[4]
    assert groups[0] != groups[3]


def test_metric_payload_reports_binary_macro_f1() -> None:
    metrics = metric_payload(pd.Series([0, 0, 1, 1]), [0, 1, 1, 1])
    assert set(metrics) == {"accuracy", "precision_macro", "recall_macro", "macro_f1"}
    assert 0 <= metrics["macro_f1"] <= 1
