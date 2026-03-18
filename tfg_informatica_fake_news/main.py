from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from preprocessing import preprocess_records
from telegram_extractor import (
    PROJECT_ROOT,
    default_channels_from_env,
    extract_messages,
    load_config_from_env,
    write_messages,
)


ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

SAMPLE_INPUT = PROJECT_ROOT / "data" / "raw" / "sample_messages.json"


def _default_output(path_env: str, relative_default: str) -> Path:
    raw = os.getenv(path_env, relative_default)
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def _load_sample_records(sample_path: Path) -> list[dict]:
    with sample_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline inicial del TFG de fake news en Telegram.")
    parser.add_argument("--channels", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=int(os.getenv("EXTRACTION_LIMIT", "25")))
    parser.add_argument("--use-sample", action="store_true")
    parser.add_argument("--sample-path", default=str(SAMPLE_INPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_output = _default_output("RAW_OUTPUT_PATH", "data/raw/extracted_messages.json")
    processed_output = _default_output("PREPROCESSED_OUTPUT_PATH", "data/processed/preprocessed_messages.json")

    use_sample = args.use_sample
    records: list[dict]

    if not use_sample:
        try:
            config = load_config_from_env()
            channels = args.channels if args.channels is not None else default_channels_from_env()
            messages = extract_messages(config, channels, limit=args.limit)
            write_messages(messages, raw_output)
            records = [message.to_dict() for message in messages]
        except ValueError:
            use_sample = True

    if use_sample:
        sample_path = Path(args.sample_path)
        if not sample_path.is_absolute():
            sample_path = PROJECT_ROOT / sample_path
        records = _load_sample_records(sample_path)
        raw_output.parent.mkdir(parents=True, exist_ok=True)
        raw_output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    processed = [item.to_dict() for item in preprocess_records(records)]
    processed_output.parent.mkdir(parents=True, exist_ok=True)
    processed_output.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK raw -> {raw_output.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"OK processed -> {processed_output.relative_to(PROJECT_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
