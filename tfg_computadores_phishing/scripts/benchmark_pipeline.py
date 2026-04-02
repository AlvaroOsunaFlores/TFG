from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import uuid

import pandas as pd
from pymongo import MongoClient

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from observability import ProcessResourceMonitor, record_benchmark_summary
from pipeline import (
    InferencePipeline,
    build_message_document,
    ensure_indexes,
    finalize_persisted_document,
    load_pipeline_settings,
)
from reporting import ensure_benchmark_dir, mirror_latest_files, relative_report_path, write_json
from scripts.simulate_cases import simulated_cases


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * quantile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    if lower == upper:
        return float(ordered[lower])
    weight = index - lower
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * weight)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark controlado del pipeline del TFG de Computadores.")
    parser.add_argument("--rates", nargs="+", type=int, default=[1, 5, 10, 20])
    parser.add_argument("--duration-seconds", type=int, default=15)
    parser.add_argument("--outdir", default=os.getenv("REPORTS_DIR", "reports"))
    parser.add_argument("--write-mongo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports_dir = Path(args.outdir)
    if not reports_dir.is_absolute():
        reports_dir = PROJECT_ROOT / reports_dir

    if args.dry_run:
        payload = {
            "rates": args.rates,
            "duration_seconds": args.duration_seconds,
            "outdir": str(reports_dir),
            "write_mongo": bool(args.write_mongo),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("OK dry-run: benchmark configurado, sin ejecutar inferencia.")
        return

    benchmark_id = f"bench-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    benchmark_dir = ensure_benchmark_dir(reports_dir, benchmark_id)

    settings = load_pipeline_settings()
    pipeline = InferencePipeline(settings)
    resource_monitor = ProcessResourceMonitor(snapshot_interval_seconds=1.0)

    mongo_collection = None
    if args.write_mongo:
        mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
        mongo_collection = mongo_client[os.getenv("MONGO_DB", "tfg")][os.getenv("MONGO_COLLECTION", "messages")]
        ensure_indexes(mongo_collection, settings.retention_days)

    sample_cases = simulated_cases()
    sample_rows: list[dict[str, object]] = []
    scenario_summaries: list[dict[str, object]] = []

    for target_rate in args.rates:
        scenario_started = time.perf_counter()
        interval = 1.0 / max(target_rate, 1)
        planned_messages = max(target_rate * args.duration_seconds, 1)
        errors = 0
        scenario_rows: list[dict[str, object]] = []

        for index in range(planned_messages):
            expected_start = scenario_started + index * interval
            remaining = expected_start - time.perf_counter()
            if remaining > 0:
                time.sleep(remaining)

            case = sample_cases[index % len(sample_cases)]
            source_received_at = datetime.now(timezone.utc).isoformat()
            snapshot = resource_monitor.snapshot(force=True)
            document = build_message_document(
                {
                    "run_id": benchmark_id,
                    "text": case.text,
                    "sender_id": f"bench-user-{index}",
                    "chat_id": f"bench-chat-{target_rate}",
                    "message_id": index + 1,
                    "channel": f"benchmark_{target_rate}msg_s",
                    "source": "benchmark",
                    "source_received_at_utc": source_received_at,
                    "queued_at_utc": source_received_at,
                },
                pipeline=pipeline,
                settings=settings,
                resource_snapshot=snapshot.to_document_fields(),
                queue_depth=0,
            )

            db_write_latency_ms = 0.0
            if mongo_collection is not None:
                try:
                    started = time.perf_counter()
                    insert_result = mongo_collection.insert_one(document)
                    db_write_latency_ms = round((time.perf_counter() - started) * 1000, 3)
                    persisted = finalize_persisted_document(document, db_write_latency_ms)
                    mongo_collection.update_one(
                        {"_id": insert_result.inserted_id},
                        {
                            "$set": {
                                "persisted_at_utc": persisted["persisted_at_utc"],
                                "db_write_latency_ms": persisted["db_write_latency_ms"],
                                "end_to_end_latency_ms": persisted["end_to_end_latency_ms"],
                            }
                        },
                    )
                    document = persisted
                except Exception:
                    errors += 1
                    document["ok"] = False
                    document["error"] = "mongo_benchmark_insert_failed"
            else:
                document = finalize_persisted_document(document, db_write_latency_ms)

            if document.get("ok") is False:
                errors += 1

            scenario_row = {
                "benchmark_id": benchmark_id,
                "target_rate_mps": target_rate,
                "message_id": document.get("message_id"),
                "pred": document.get("pred"),
                "score_1": document.get("score_1"),
                "preprocess_latency_ms": document.get("preprocess_latency_ms"),
                "inference_latency_ms": document.get("inference_latency_ms"),
                "db_write_latency_ms": document.get("db_write_latency_ms"),
                "end_to_end_latency_ms": document.get("end_to_end_latency_ms"),
                "cpu_percent": document.get("cpu_percent"),
                "rss_bytes": document.get("rss_bytes"),
                "vms_bytes": document.get("vms_bytes"),
                "gpu_memory_bytes": document.get("gpu_memory_bytes"),
                "ok": document.get("ok"),
            }
            scenario_rows.append(scenario_row)
            sample_rows.append(scenario_row)

        elapsed = max(time.perf_counter() - scenario_started, 0.001)
        e2e_latencies = [
            float(row["end_to_end_latency_ms"])
            for row in scenario_rows
            if isinstance(row.get("end_to_end_latency_ms"), (int, float))
        ]
        cpu_samples = [float(row["cpu_percent"]) for row in scenario_rows if isinstance(row.get("cpu_percent"), (int, float))]
        rss_samples = [float(row["rss_bytes"]) for row in scenario_rows if isinstance(row.get("rss_bytes"), (int, float))]
        vms_samples = [float(row["vms_bytes"]) for row in scenario_rows if isinstance(row.get("vms_bytes"), (int, float))]

        summary = {
            "scenario": f"{target_rate}msg_s",
            "target_rate_mps": target_rate,
            "planned_messages": planned_messages,
            "processed_messages": len(scenario_rows),
            "throughput_mps": round(len(scenario_rows) / elapsed, 3),
            "latency_avg_ms": round(sum(e2e_latencies) / len(e2e_latencies), 3) if e2e_latencies else None,
            "latency_p95_ms": _percentile(e2e_latencies, 0.95),
            "cpu_avg_percent": round(sum(cpu_samples) / len(cpu_samples), 3) if cpu_samples else None,
            "ram_avg_bytes": round(sum(rss_samples) / len(rss_samples), 3) if rss_samples else None,
            "vms_avg_bytes": round(sum(vms_samples) / len(vms_samples), 3) if vms_samples else None,
            "error_rate": round(errors / max(len(scenario_rows), 1), 5),
        }
        scenario_summaries.append(summary)
        record_benchmark_summary(summary["scenario"], summary)

    samples_path = benchmark_dir / "benchmark_samples.csv"
    pd.DataFrame(sample_rows).to_csv(samples_path, index=False)

    summary_path = benchmark_dir / "benchmark_summary.json"
    payload = {
        "benchmark_id": benchmark_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds_per_scenario": args.duration_seconds,
        "write_mongo": bool(args.write_mongo),
        "artifacts_dir": relative_report_path(benchmark_dir, reports_dir),
        "scenarios": scenario_summaries,
        "artifacts": {
            "samples_csv": relative_report_path(samples_path, reports_dir),
            "summary_json": relative_report_path(summary_path, reports_dir),
        },
    }
    write_json(summary_path, payload)
    mirror_latest_files(benchmark_dir, reports_dir, ["benchmark_summary.json"])
    print(f"OK -> {relative_report_path(summary_path, reports_dir)}")


if __name__ == "__main__":
    main()
