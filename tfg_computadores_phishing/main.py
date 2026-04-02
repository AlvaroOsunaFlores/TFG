from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import time

from dotenv import load_dotenv
from pymongo import MongoClient
from telethon import TelegramClient, events
import telethon

from pipeline import (
    InferencePipeline,
    build_message_document,
    ensure_indexes,
    finalize_persisted_document,
    load_pipeline_settings,
)
from producer import run_producer
from worker import run_worker


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Falta la variable de entorno obligatoria: {name}")
    return value.strip()


async def run_legacy_mode() -> None:
    api_id = int(_required_env("TELEGRAM_API_ID"))
    api_hash = _required_env("TELEGRAM_API_HASH")
    phone = _required_env("TELEGRAM_PHONE")

    settings = load_pipeline_settings()
    pipeline = InferencePipeline(settings)
    mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    collection = mongo[os.getenv("MONGO_DB", "tfg")][os.getenv("MONGO_COLLECTION", "messages")]
    ensure_indexes(collection, settings.retention_days)

    session_path = PROJECT_ROOT / "session" / "study_Session"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(session_path), api_id, api_hash)

    await client.connect()
    if not await client.is_user_authorized():
        print("Enviando codigo...")
        await client.send_code_request(phone)
        code = input("Introduce el codigo enviado por Telegram: ")
        try:
            await client.sign_in(phone, code)
        except telethon.errors.SessionPasswordNeededError:
            password = input("Introduce tu password de 2FA: ")
            await client.sign_in(password=password)

    me = await client.get_me()
    username = getattr(me, "username", None)
    print(f"Legacy conectado como {me.first_name} (@{username})")
    print("Modo legacy -> Telegram -> clasificacion -> MongoDB")

    @client.on(events.NewMessage)
    async def handler(event) -> None:
        msg = event.message.text or ""
        if not msg.strip():
            return

        payload = {
            "run_id": os.getenv("RUN_ID"),
            "text": msg,
            "sender_id": getattr(event.message, "sender_id", None),
            "chat_id": getattr(event, "chat_id", None),
            "message_id": getattr(event.message, "id", None),
            "channel": getattr(getattr(event, "chat", None), "title", None),
            "source": "legacy_main",
            "source_received_at_utc": getattr(event.message, "date", None).isoformat() if getattr(event.message, "date", None) else None,
            "queued_at_utc": None,
        }
        document = build_message_document(payload, pipeline=pipeline, settings=settings)
        started = time.perf_counter()
        result = collection.insert_one(document)
        db_write_latency_ms = round((time.perf_counter() - started) * 1000, 3)
        persisted = finalize_persisted_document(document, db_write_latency_ms)
        collection.update_one(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "persisted_at_utc": persisted["persisted_at_utc"],
                    "db_write_latency_ms": persisted["db_write_latency_ms"],
                    "end_to_end_latency_ms": persisted["end_to_end_latency_ms"],
                }
            },
        )
        print(
            "Legacy guardado -> "
            f"message_id={persisted.get('message_id')}, "
            f"pred={persisted.get('pred')}, "
            f"e2e_ms={persisted.get('end_to_end_latency_ms')}"
        )

    await client.run_until_disconnected()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entry point del TFG de Computadores.")
    parser.add_argument(
        "--mode",
        choices=["legacy", "producer", "worker"],
        default=os.getenv("APP_MODE", "legacy"),
        help="Modo de ejecucion. legacy mantiene el flujo anterior; producer/worker usan RabbitMQ.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "producer":
        asyncio.run(run_producer())
        return
    if args.mode == "worker":
        run_worker()
        return
    asyncio.run(run_legacy_mode())


if __name__ == "__main__":
    main()
