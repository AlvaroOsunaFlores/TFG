from __future__ import annotations

import json
from pathlib import Path
import shutil


def ensure_reports_dir(reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def ensure_run_dir(reports_dir: Path, run_id: str) -> Path:
    run_dir = ensure_reports_dir(reports_dir) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def ensure_validation_dir(reports_dir: Path, validation_id: str) -> Path:
    validation_dir = ensure_reports_dir(reports_dir) / "validations" / validation_id
    validation_dir.mkdir(parents=True, exist_ok=True)
    return validation_dir


def relative_report_path(path: Path, reports_dir: Path) -> str:
    return path.resolve().relative_to(reports_dir.resolve()).as_posix()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def mirror_latest_files(run_dir: Path, reports_dir: Path, filenames: list[str]) -> None:
    ensure_reports_dir(reports_dir)
    for filename in filenames:
        source = run_dir / filename
        if source.exists():
            shutil.copy2(source, reports_dir / filename)


def sanitize_display_command(command: list[str]) -> str:
    if not command:
        return ""

    display = command[:]
    executable = Path(display[0])
    if executable.suffix.lower() in {".exe", ".bat", ".cmd"} or "\\" in display[0] or "/" in display[0]:
        display[0] = "python"
    return " ".join(display)
