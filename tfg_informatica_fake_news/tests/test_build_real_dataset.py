from __future__ import annotations

import csv
import io
from pathlib import Path
import zipfile

from scripts.build_real_dataset import FIELDNAMES, build_real_dataset
from scripts.validate_dataset import load_dataset, validate_dataframe


def _csv_payload(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _tsv_payload(rows: list[list[str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue()


def _write_archives(root: Path) -> None:
    archive2 = root / "archive2.zip"
    with zipfile.ZipFile(archive2, "w") as zf:
        zf.writestr(
            "News _dataset/Fake.csv",
            _csv_payload(
                ["title", "text", "subject", "date"],
                [
                    {
                        "title": "Fake warning spreads online",
                        "text": "This article invents a ban and asks users to share it without evidence.",
                        "subject": "News",
                        "date": "January 1, 2024",
                    }
                ],
            ),
        )
        zf.writestr(
            "News _dataset/True.csv",
            _csv_payload(
                ["title", "text", "subject", "date"],
                [
                    {
                        "title": "Official correction published",
                        "text": "The ministry published documents that disprove the viral rumor.",
                        "subject": "politicsNews",
                        "date": "January 2, 2024",
                    }
                ],
            ),
        )

    archive = root / "archive.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(
            "train.tsv",
            _tsv_payload(
                [
                    ["1.json", "false", "The rumor is false and has no evidence at all.", "politics", "", "", "", "", "", "", "", "", "", ""],
                ]
            ),
        )
        zf.writestr(
            "valid.tsv",
            _tsv_payload(
                [
                    ["2.json", "true", "Officials confirmed the verified report with signed documents.", "economy", "", "", "", "", "", "", "", "", "", ""],
                ]
            ),
        )
        zf.writestr(
            "test.tsv",
            _tsv_payload(
                [
                    ["3.json", "half-true", "This row must be excluded from the binary mapping.", "health", "", "", "", "", "", "", "", "", "", ""],
                    ["4.json", "pants-fire", "The chain message is fabricated and completely false.", "media", "", "", "", "", "", "", "", "", "", ""],
                ]
            ),
        )


def test_build_real_dataset_creates_expected_gzip_and_metadata(tmp_path: Path) -> None:
    source_root = tmp_path / "dataset_sources"
    source_root.mkdir()
    _write_archives(source_root)

    output_path = tmp_path / "fake_news_unified.csv.gz"
    metadata_path = tmp_path / "fake_news_unified.metadata.json"

    output_file, metadata_file, metadata = build_real_dataset(source_root, output_path, metadata_path)

    assert output_file == output_path
    assert metadata_file == metadata_path
    assert metadata["rows_written"] == 5
    assert metadata["liar"]["excluded_labels"]["half-true"] == 1

    df = load_dataset(output_path)
    errors, warnings = validate_dataframe(df)

    assert errors == []
    assert isinstance(warnings, list)
    assert list(df.columns) == FIELDNAMES
    assert set(df["label"]) == {0, 1}
    assert "half-true" not in set(df["original_label"])
    assert df[df["dataset_name"] == "liar_politifact"]["date_utc"].eq("").all()
