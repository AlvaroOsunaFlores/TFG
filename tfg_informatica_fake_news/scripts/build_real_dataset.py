from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import unicodedata
import zipfile
from typing import Any

import pandas as pd

from analysis_utils import build_dataset_summary
from experiment_registry import dataset_sha256
from preprocessing import describe_cleaning_rules, preprocess_record
from scripts.validate_dataset import LABEL_NAMES, REQUIRED_COLUMNS, load_dataset, validate_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[2]
DEFAULT_SOURCE_ROOT = WORKSPACE_ROOT / "datos_entrenamiento" / "tfg_informatica_fake_news"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "labeled" / "fake_news_unified.csv.gz"
DEFAULT_METADATA_OUTPUT = PROJECT_ROOT / "data" / "labeled" / "fake_news_unified.metadata.json"

ARCHIVE2_PATH = "archive2.zip"
LIAR_PATH = "archive.zip"

EXTRA_COLUMNS = [
    "dataset_name",
    "dataset_split",
    "original_label",
    "title",
    "topic",
]

FIELDNAMES = REQUIRED_COLUMNS + EXTRA_COLUMNS

ARCHIVE2_SPECS = [
    ("News _dataset/Fake.csv", 1, "fake"),
    ("News _dataset/True.csv", 0, "real"),
]

LIAR_LABEL_MAPPING = {
    "true": 0,
    "false": 1,
    "pants-fire": 1,
}

LIAR_EXCLUDED_LABELS = {
    "half-true",
    "mostly-true",
    "barely-true",
}


def _slugify(text: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return slug or fallback


def _display_path(path: Path) -> str:
    for base_path in [PROJECT_ROOT, WORKSPACE_ROOT]:
        try:
            return path.relative_to(base_path).as_posix()
        except ValueError:
            continue
    return path.name


def _normalize_date(raw_date: str) -> str:
    raw_value = str(raw_date or "").strip()
    if not raw_value:
        return ""

    parsed = pd.to_datetime(raw_value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.isoformat()


def _make_record(
    *,
    source_id: str,
    channel: str,
    date_utc: str,
    text: str,
    label: int,
    source: str,
    dataset_name: str,
    dataset_split: str,
    original_label: str,
    title: str,
    topic: str,
    message_id: int,
) -> dict[str, Any]:
    processed = preprocess_record(
        {
            "message_id": message_id,
            "channel": channel,
            "text": text,
        }
    )
    return {
        "source_id": source_id,
        "channel": channel,
        "date_utc": date_utc,
        "text": text,
        "normalized_text": processed.normalized_text,
        "language": processed.language,
        "label": label,
        "label_name": LABEL_NAMES[label],
        "source": source,
        "dataset_name": dataset_name,
        "dataset_split": dataset_split,
        "original_label": original_label,
        "title": title,
        "topic": topic,
    }


def _build_archive2_rows(source_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archive_path = source_root / ARCHIVE2_PATH
    if not archive_path.exists():
        raise FileNotFoundError(f"No se encuentra {archive_path}")

    rows: list[dict[str, Any]] = []
    per_label = Counter()
    per_file = Counter()
    skipped_empty = 0

    with zipfile.ZipFile(archive_path) as zf:
        for entry_name, label, original_label in ARCHIVE2_SPECS:
            with zf.open(entry_name) as handle:
                reader = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8"))
                for index, row in enumerate(reader, start=1):
                    title = str(row.get("title", "")).strip()
                    body = str(row.get("text", "")).strip()
                    combined_text = "\n\n".join(part for part in [title, body] if part)
                    if not combined_text:
                        skipped_empty += 1
                        continue

                    topic = str(row.get("subject", "")).strip()
                    channel = f"archive2_{_slugify(topic, 'external')}"
                    rows.append(
                        _make_record(
                            source_id=f"archive2-{original_label}-{index:05d}",
                            channel=channel,
                            date_utc=_normalize_date(str(row.get("date", ""))),
                            text=combined_text,
                            label=label,
                            source="archive2_news_dataset",
                            dataset_name="archive2_news_dataset",
                            dataset_split="full",
                            original_label=original_label,
                            title=title,
                            topic=topic,
                            message_id=index,
                        )
                    )
                    per_label[original_label] += 1
                    per_file[entry_name] += 1

    metadata = {
        "rows_written": sum(per_label.values()),
        "per_label": dict(per_label),
        "per_file": dict(per_file),
        "skipped_empty": skipped_empty,
    }
    return rows, metadata


def _build_liar_rows(source_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    archive_path = source_root / LIAR_PATH
    if not archive_path.exists():
        raise FileNotFoundError(f"No se encuentra {archive_path}")

    rows: list[dict[str, Any]] = []
    included_labels = Counter()
    excluded_labels = Counter()
    skipped_empty = 0
    split_counts = Counter()

    with zipfile.ZipFile(archive_path) as zf:
        for split_name in ["train", "valid", "test"]:
            with zf.open(f"{split_name}.tsv") as handle:
                reader = csv.reader(io.TextIOWrapper(handle, encoding="utf-8"), delimiter="\t")
                for row in reader:
                    if len(row) < 4:
                        skipped_empty += 1
                        continue

                    original_label = str(row[1]).strip()
                    if original_label in LIAR_EXCLUDED_LABELS:
                        excluded_labels[original_label] += 1
                        continue
                    if original_label not in LIAR_LABEL_MAPPING:
                        excluded_labels[original_label] += 1
                        continue

                    statement = str(row[2]).strip()
                    if not statement:
                        skipped_empty += 1
                        continue

                    topic = str(row[3]).strip()
                    label = LIAR_LABEL_MAPPING[original_label]
                    source_id = str(row[0]).replace(".json", "").strip()
                    rows.append(
                        _make_record(
                            source_id=f"liar-{split_name}-{source_id}",
                            channel="liar_politifact",
                            date_utc="",
                            text=statement,
                            label=label,
                            source="liar_politifact",
                            dataset_name="liar_politifact",
                            dataset_split=split_name,
                            original_label=original_label,
                            title="",
                            topic=topic,
                            message_id=len(rows) + 1,
                        )
                    )
                    included_labels[original_label] += 1
                    split_counts[split_name] += 1

    metadata = {
        "rows_written": sum(included_labels.values()),
        "per_label": dict(included_labels),
        "excluded_labels": dict(excluded_labels),
        "per_split": dict(split_counts),
        "skipped_empty": skipped_empty,
    }
    return rows, metadata


def write_dataset(rows: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows, columns=FIELDNAMES)
    frame.to_csv(output_path, index=False, compression="infer")
    return output_path


def build_real_dataset(
    source_root: Path,
    output_path: Path = DEFAULT_OUTPUT,
    metadata_output_path: Path = DEFAULT_METADATA_OUTPUT,
) -> tuple[Path, Path, dict[str, Any]]:
    archive2_rows, archive2_meta = _build_archive2_rows(source_root)
    liar_rows, liar_meta = _build_liar_rows(source_root)

    rows = archive2_rows + liar_rows
    rows.sort(key=lambda item: item["source_id"])
    write_dataset(rows, output_path)

    dataset_df = load_dataset(output_path)
    errors, warnings = validate_dataframe(dataset_df)
    if errors:
        raise ValueError(f"El dataset real generado no es valido: {errors}")

    dataset_summary = build_dataset_summary(dataset_df)
    dataset_name_distribution = {
        str(key): int(value)
        for key, value in dataset_df["dataset_name"].value_counts().sort_index().items()
    }
    empty_rows_skipped = {
        "archive2": int(archive2_meta["skipped_empty"]),
        "liar": int(liar_meta["skipped_empty"]),
        "total": int(archive2_meta["skipped_empty"] + liar_meta["skipped_empty"]),
    }

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": _display_path(source_root),
        "output_path": _display_path(output_path),
        "archives_used": [ARCHIVE2_PATH, LIAR_PATH],
        "archives_excluded": ["archive3.zip"],
        "rows_written": int(len(dataset_df)),
        "label_distribution": dataset_summary["label_distribution"],
        "dataset_name_distribution": dataset_name_distribution,
        "language_distribution": dataset_summary["language_distribution"],
        "included_languages": dataset_summary["included_languages"],
        "text_length_summary": dataset_summary["text_length_summary"],
        "cleaning_rules": describe_cleaning_rules(),
        "exclusion_rules": {
            "archives_excluded": ["archive3.zip"],
            "liar_labels_excluded": sorted(LIAR_EXCLUDED_LABELS),
            "liar_excluded_label_counts": liar_meta["excluded_labels"],
            "empty_rows_skipped": empty_rows_skipped,
        },
        "archive2": archive2_meta,
        "liar": liar_meta,
        "warnings": warnings,
        "schema": FIELDNAMES,
    }
    metadata["dataset_sha256"] = dataset_sha256(output_path)

    metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_output_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path, metadata_output_path, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unifica datasets reales de fake news en un corpus canonico comprimido.")
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--metadata-output", default=str(DEFAULT_METADATA_OUTPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_root = Path(args.source_root)
    output_path = Path(args.output)
    metadata_output_path = Path(args.metadata_output)

    if not source_root.is_absolute():
        source_root = PROJECT_ROOT / source_root
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    if not metadata_output_path.is_absolute():
        metadata_output_path = PROJECT_ROOT / metadata_output_path

    output_path, metadata_output_path, metadata = build_real_dataset(
        source_root=source_root,
        output_path=output_path,
        metadata_output_path=metadata_output_path,
    )

    print(f"OK dataset real -> {_display_path(output_path)}")
    print(f"OK metadata -> {_display_path(metadata_output_path)}")
    print(
        "Filas: "
        f"{metadata['rows_written']} | "
        f"labels={metadata['label_distribution']} | "
        f"fuentes={metadata['dataset_name_distribution']}"
    )


if __name__ == "__main__":
    main()
