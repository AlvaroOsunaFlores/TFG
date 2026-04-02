from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dataset_manager import deduplicate_records, resolve_project_path, write_json_payload
from preprocessing import preprocess_records


@dataclass(frozen=True)
class PipelinePaths:
    raw_output: Path
    processed_output: Path
    registry_path: Path
    manifest_output: Path


def default_pipeline_paths(
    *,
    raw_output: str | Path = "data/raw/extracted_messages.json",
    processed_output: str | Path = "data/processed/preprocessed_messages.json",
    registry_path: str | Path = "data/raw/extraction_registry.json",
    manifest_output: str | Path = "reports/pipeline_runs/latest_pipeline_manifest.json",
) -> PipelinePaths:
    return PipelinePaths(
        raw_output=resolve_project_path(raw_output),
        processed_output=resolve_project_path(processed_output),
        registry_path=resolve_project_path(registry_path),
        manifest_output=resolve_project_path(manifest_output),
    )


def run_pipeline(
    records: list[dict[str, Any]],
    *,
    paths: PipelinePaths,
    source_mode: str,
    extraction_failures: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    deduplicated, duplicate_count = deduplicate_records(records, paths.registry_path)
    processed = [item.to_dict() for item in preprocess_records(deduplicated)]

    write_json_payload(paths.raw_output, deduplicated)
    write_json_payload(paths.processed_output, processed)

    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_mode": source_mode,
        "raw_output": str(paths.raw_output),
        "processed_output": str(paths.processed_output),
        "registry_path": str(paths.registry_path),
        "input_records": len(records),
        "deduplicated_records": len(deduplicated),
        "duplicate_records": duplicate_count,
        "processed_records": len(processed),
        "extraction_failures": extraction_failures or [],
    }
    write_json_payload(paths.manifest_output, payload)
    return payload
