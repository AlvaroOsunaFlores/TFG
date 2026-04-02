from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from pipeline import default_pipeline_paths, run_pipeline
from telegram_extractor import (
    PROJECT_ROOT,
    default_channels_from_env,
    extract_messages_with_report,
    load_config_from_env,
)


ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

SAMPLE_INPUT = PROJECT_ROOT / "data" / "raw" / "sample_messages.json"


def _load_sample_records(sample_path: Path) -> list[dict]:
    with sample_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline reproducible del TFG de fake news en Telegram.")
    parser.add_argument("--channels", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=int(os.getenv("EXTRACTION_LIMIT", "25")))
    parser.add_argument("--use-sample", action="store_true")
    parser.add_argument("--sample-path", default=str(SAMPLE_INPUT))
    parser.add_argument("--raw-output", default="data/raw/extracted_messages.json")
    parser.add_argument("--processed-output", default="data/processed/preprocessed_messages.json")
    parser.add_argument("--registry-path", default="data/raw/extraction_registry.json")
    parser.add_argument("--manifest-output", default="reports/pipeline_runs/latest_pipeline_manifest.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = default_pipeline_paths(
        raw_output=args.raw_output,
        processed_output=args.processed_output,
        registry_path=args.registry_path,
        manifest_output=args.manifest_output,
    )

    extraction_failures: list[dict[str, str]] = []
    if args.use_sample:
        sample_path = Path(args.sample_path)
        if not sample_path.is_absolute():
            sample_path = PROJECT_ROOT / sample_path
        records = _load_sample_records(sample_path)
        source_mode = "sample"
    else:
        try:
            config = load_config_from_env()
            channels = args.channels if args.channels is not None else default_channels_from_env()
            extraction = extract_messages_with_report(config, channels, limit=args.limit)
            records = [message.to_dict() for message in extraction.messages]
            extraction_failures = extraction.failed_channels
            source_mode = "telegram"
        except ValueError:
            sample_path = Path(args.sample_path)
            if not sample_path.is_absolute():
                sample_path = PROJECT_ROOT / sample_path
            records = _load_sample_records(sample_path)
            source_mode = "sample_fallback"

    manifest = run_pipeline(records, paths=paths, source_mode=source_mode, extraction_failures=extraction_failures)
    print(f"OK raw -> {paths.raw_output.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"OK processed -> {paths.processed_output.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"OK manifest -> {paths.manifest_output.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"Deduplicados: {manifest['duplicate_records']} | Procesados: {manifest['processed_records']}")


if __name__ == "__main__":
    main()
