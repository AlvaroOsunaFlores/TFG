from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


def run_command(command: list[str], env: dict[str, str]) -> dict[str, str | int]:
    started = datetime.now(timezone.utc)
    process = subprocess.run(command, capture_output=True, text=True, env=env)
    return {
        "command": " ".join(command),
        "returncode": process.returncode,
        "stdout": process.stdout[-2000:],
        "stderr": process.stderr[-2000:],
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Runner de validacion Fase 5 (integracion + E2E).")
    parser.add_argument("--threshold", default="0.05")
    parser.add_argument("--outdir", default="reports")
    parser.add_argument("--skip-evaluate", action="store_true")
    parser.add_argument("--write-mongo", action="store_true")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["THRESHOLD"] = str(args.threshold)

    steps: list[dict[str, str | int]] = []

    if not args.skip_evaluate:
        steps.append(run_command([sys.executable, "evaluate.py"], env))

    sim_cmd = [sys.executable, "scripts/simulate_cases.py", "--threshold", str(args.threshold), "--outdir", str(outdir)]
    if args.write_mongo:
        sim_cmd.append("--write-mongo")
    steps.append(run_command(sim_cmd, env))

    expected_files = [
        outdir / "metrics.json",
        outdir / "confusion_matrix.csv",
        outdir / "predictions.csv",
        outdir / "threshold_analysis.csv",
        outdir / "simulated_cases_results.csv",
        outdir / "e2e_evidence.json",
    ]
    files_status = {str(path): path.exists() for path in expected_files}

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "threshold_used": float(args.threshold),
        "steps": steps,
        "files_status": files_status,
        "all_steps_ok": all(step["returncode"] == 0 for step in steps),
        "all_files_present": all(files_status.values()),
    }

    out_path = outdir / "phase5_validation.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
