from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _split_csv(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    items = [value.strip() for value in raw.split(",")]
    return [value for value in items if value]


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Falta la variable de entorno obligatoria: {name}")
    return value.strip()


def _path_from_env(name: str, default_relative: str) -> Path:
    raw = os.getenv(name, default_relative)
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


@dataclass(frozen=True)
class Settings:
    reports_dir: Path
    mongo_uri: str
    mongo_db: str
    mongo_collection: str
    training_metadata_path: Path
    cors_origins: list[str]
    api_key: str


def load_settings() -> Settings:
    reports_dir = _path_from_env("REPORTS_DIR", "reports")
    metadata_path = _path_from_env("TRAINING_METADATA_PATH", "docs/training_metadata.json")

    return Settings(
        reports_dir=reports_dir,
        mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        mongo_db=os.getenv("MONGO_DB", "tfg"),
        mongo_collection=os.getenv("MONGO_COLLECTION", "messages"),
        training_metadata_path=metadata_path,
        cors_origins=_split_csv(os.getenv("API_CORS_ORIGINS")),
        api_key=_required_env("API_KEY"),
    )
