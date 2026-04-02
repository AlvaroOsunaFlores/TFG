from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_project_path(raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def build_source_id(record: dict[str, Any]) -> str:
    channel = str(record.get("channel", "unknown")).strip() or "unknown"
    message_id = str(record.get("message_id", "0")).strip() or "0"
    return f"{channel}:{message_id}"


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"created_at_utc": datetime.now(timezone.utc).isoformat(), "seen_source_ids": []}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_registry(path: Path, registry: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def deduplicate_records(records: list[dict[str, Any]], registry_path: Path) -> tuple[list[dict[str, Any]], int]:
    registry = load_registry(registry_path)
    seen = set(registry.get("seen_source_ids", []))
    deduplicated: list[dict[str, Any]] = []
    duplicates = 0

    for record in records:
        source_id = str(record.get("source_id") or build_source_id(record))
        if source_id in seen:
            duplicates += 1
            continue
        enriched = dict(record)
        enriched["source_id"] = source_id
        deduplicated.append(enriched)
        seen.add(source_id)

    registry["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    registry["seen_source_ids"] = sorted(seen)
    save_registry(registry_path, registry)
    return deduplicated, duplicates


def write_json_payload(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
