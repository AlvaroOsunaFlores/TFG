from pathlib import Path

from scripts.build_seed_dataset import build_seed_rows, write_dataset
from scripts.validate_dataset import REQUIRED_COLUMNS, load_dataset, validate_dataframe


def test_build_seed_rows_returns_expected_schema_and_both_labels() -> None:
    rows = build_seed_rows()

    assert rows
    assert set(REQUIRED_COLUMNS).issubset(rows[0].keys())
    assert {row["label"] for row in rows} == {0, 1}
    assert all(row["label_name"] for row in rows)


def test_written_seed_dataset_passes_validation(tmp_path: Path) -> None:
    output_path = tmp_path / "fake_news_seed.csv"
    write_dataset(build_seed_rows(), output_path)

    df = load_dataset(output_path)
    errors, warnings = validate_dataframe(df)

    assert errors == []
    assert isinstance(warnings, list)
