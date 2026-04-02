from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
import telethon

from messaging import load_rabbitmq_settings, publish_json_message
from observability import record_publish
from pipeline import build_queue_payload, generate_run_id


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Falta la variable de entorno obligatoria: {name}")
    return value.strip()


async def run_producer() -> None:
    api_id = int(_required_env("TELEGRAM_API_ID"))
    api_hash = _required_env("TELEGRAM_API_HASH")
    phone = _required_env("TELEGRAM_PHONE")
    rabbit_settings = load_rabbitmq_settings()
    run_id = generate_run_id()

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
    print(f"Producer conectado como {me.first_name} (@{username})")
    print(f"RUN_ID={run_id}")

    @client.on(events.NewMessage)
    async def handler(event) -> None:
        msg = event.message.text or ""
        if not msg.strip():
            return

        source_received_at_utc = getattr(event.message, "date", None)
        source_received = source_received_at_utc.isoformat() if source_received_at_utc else None
        payload = build_queue_payload(
            text=msg,
            sender_id=getattr(event.message, "sender_id", None),
            chat_id=getattr(event, "chat_id", None),
            message_id=getattr(event.message, "id", None),
            channel=getattr(getattr(event, "chat", None), "title", None),
            run_id=run_id,
            source="telegram_producer",
            source_received_at_utc=source_received,
        )
        queue_depth = publish_json_message(payload, rabbit_settings)
        record_publish(source="telegram_producer", queue_depth=queue_depth)
        print(
            "Publicado -> "
            f"message_id={payload.get('message_id')}, "
            f"queue_depth={queue_depth}, "
            f"chat={payload.get('channel') or payload.get('chat_id')}"
        )

    print("Producer escuchando mensajes y publicando en RabbitMQ...")
    await client.run_until_disconnected()


def main() -> None:
    asyncio.run(run_producer())


if __name__ == "__main__":
    main()
