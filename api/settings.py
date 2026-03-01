from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _split_csv(raw: str | None) -> list[str]:
    if not raw:
        return ["*"]
    items = [value.strip() for value in raw.split(",")]
    return [value for value in items if value]


@dataclass(frozen=True)
class Settings:
    reports_dir: Path
    mongo_uri: str
    mongo_db: str
    mongo_collection: str
    training_metadata_path: Path
    cors_origins: list[str]


def load_settings() -> Settings:
    reports_dir = Path(os.getenv("REPORTS_DIR", "reports"))
    metadata_path = Path(os.getenv("TRAINING_METADATA_PATH", "docs/training_metadata.json"))

    return Settings(
        reports_dir=reports_dir,
        mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        mongo_db=os.getenv("MONGO_DB", "tfg"),
        mongo_collection=os.getenv("MONGO_COLLECTION", "messages"),
        training_metadata_path=metadata_path,
        cors_origins=_split_csv(os.getenv("API_CORS_ORIGINS")),
    )
