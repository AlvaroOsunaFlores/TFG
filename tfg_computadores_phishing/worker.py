from __future__ import annotations

import os
from pathlib import Path
import time

from dotenv import load_dotenv
from prometheus_client import start_http_server
from pymongo import MongoClient

from messaging import consume_json_messages, get_queue_depth, load_rabbitmq_settings
from observability import ProcessResourceMonitor, record_queue_depth, record_worker_result
from pipeline import (
    InferencePipeline,
    build_message_document,
    ensure_indexes,
    finalize_persisted_document,
    load_pipeline_settings,
)


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)


def _mongo_client_from_env() -> MongoClient:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    return MongoClient(mongo_uri)


def run_worker() -> None:
    settings = load_pipeline_settings()
    rabbit_settings = load_rabbitmq_settings()
    resource_monitor = ProcessResourceMonitor(snapshot_interval_seconds=float(os.getenv("RESOURCE_SNAPSHOT_SECONDS", "5")))
    pipeline = InferencePipeline(settings)

    mongo_client = _mongo_client_from_env()
    mongo_db = os.getenv("MONGO_DB", "tfg")
    mongo_collection = os.getenv("MONGO_COLLECTION", "messages")
    collection = mongo_client[mongo_db][mongo_collection]
    ensure_indexes(collection, settings.retention_days)

    metrics_port = int(os.getenv("WORKER_METRICS_PORT", "9108"))
    start_http_server(metrics_port)
    print(f"Worker metrics -> http://0.0.0.0:{metrics_port}/metrics")

    def _handle(payload: dict[str, object]) -> None:
        queue_depth = get_queue_depth(rabbit_settings)
        record_queue_depth(queue_depth)
        snapshot = resource_monitor.snapshot(force=False)
        document = build_message_document(
            payload,
            pipeline=pipeline,
            settings=settings,
            resource_snapshot=snapshot.to_document_fields(),
            queue_depth=queue_depth,
        )

        inserted_id = None
        started = time.perf_counter()
        result = collection.insert_one(document)
        db_write_latency_ms = round((time.perf_counter() - started) * 1000, 3)
        inserted_id = result.inserted_id

        persisted = finalize_persisted_document(document, db_write_latency_ms)
        collection.update_one(
            {"_id": inserted_id},
            {
                "$set": {
                    "persisted_at_utc": persisted["persisted_at_utc"],
                    "db_write_latency_ms": persisted["db_write_latency_ms"],
                    "end_to_end_latency_ms": persisted["end_to_end_latency_ms"],
                }
            },
        )
        record_worker_result(persisted)

        print(
            "Procesado -> "
            f"message_id={persisted.get('message_id')}, "
            f"pred={persisted.get('pred')}, "
            f"queue_depth={persisted.get('queue_depth')}, "
            f"e2e_ms={persisted.get('end_to_end_latency_ms')}"
        )

    print("Worker escuchando RabbitMQ y persistiendo en MongoDB...")
    consume_json_messages(rabbit_settings, _handle)


def main() -> None:
    run_worker()


if __name__ == "__main__":
    main()
