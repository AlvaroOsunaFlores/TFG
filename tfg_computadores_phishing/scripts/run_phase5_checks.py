from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reporting import ensure_validation_dir, relative_report_path, sanitize_display_command, write_json


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str], env: dict[str, str], reports_dir: Path) -> dict[str, str | int]:
    started = datetime.now(timezone.utc)
    process = subprocess.run(command, capture_output=True, text=True, env=env, cwd=REPO_ROOT)
    return {
        "command": sanitize_display_command(command),
        "returncode": process.returncode,
        "stdout": process.stdout[-2000:],
        "stderr": process.stderr[-2000:],
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "reports_dir": relative_report_path(reports_dir, reports_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Runner de validacion Fase 5 (integracion + E2E).")
    parser.add_argument("--threshold", default="0.05")
    parser.add_argument("--outdir", default="reports")
    parser.add_argument("--skip-evaluate", action="store_true")
    parser.add_argument("--write-mongo", action="store_true")
    args = parser.parse_args()

    reports_dir = Path(args.outdir)
    if not reports_dir.is_absolute():
        reports_dir = REPO_ROOT / reports_dir
    validation_id = f"phase5-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    validation_dir = ensure_validation_dir(reports_dir, validation_id)

    env = dict(os.environ)
    env["THRESHOLD"] = str(args.threshold)
    env["CUDA_VISIBLE_DEVICES"] = ""

    steps: list[dict[str, str | int]] = []

    if not args.skip_evaluate:
        steps.append(run_command([sys.executable, "evaluate.py"], env, reports_dir))

    sim_cmd = [sys.executable, "-m", "scripts.simulate_cases", "--threshold", str(args.threshold), "--outdir", str(reports_dir)]
    if args.write_mongo:
        sim_cmd.append("--write-mongo")
    steps.append(run_command(sim_cmd, env, reports_dir))

    expected_files = [
        reports_dir / "metrics.json",
        reports_dir / "confusion_matrix.csv",
        reports_dir / "predictions.csv",
        reports_dir / "threshold_analysis.csv",
        reports_dir / "simulated_cases_results.csv",
        reports_dir / "e2e_evidence.json",
    ]
    files_status = {relative_report_path(path, reports_dir): path.exists() for path in expected_files}

    payload = {
        "validation_id": validation_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "threshold_used": float(args.threshold),
        "steps": steps,
        "files_status": files_status,
        "all_steps_ok": all(step["returncode"] == 0 for step in steps),
        "all_files_present": all(files_status.values()),
        "artifacts_dir": relative_report_path(validation_dir, reports_dir),
    }

    out_path = validation_dir / "phase5_validation.json"
    write_json(out_path, payload)
    write_json(reports_dir / "phase5_validation.json", payload)

    print(f"OK -> {relative_report_path(out_path, reports_dir)}")


if __name__ == "__main__":
    main()
