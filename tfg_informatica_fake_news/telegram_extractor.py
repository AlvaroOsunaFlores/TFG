from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Iterable, Sequence

from dotenv import load_dotenv
from telethon import TelegramClient


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class TelegramConfig:
    api_id: int
    api_hash: str
    session_name: str


@dataclass(frozen=True)
class TelegramMessage:
    message_id: int
    chat_id: int | None
    chat_title: str | None
    channel: str
    sender_id: int | None
    date_utc: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Falta la variable de entorno obligatoria: {name}")
    return value


def load_config_from_env() -> TelegramConfig:
    return TelegramConfig(
        api_id=int(_required_env("TELEGRAM_API_ID")),
        api_hash=_required_env("TELEGRAM_API_HASH"),
        session_name=os.getenv("TELEGRAM_SESSION_NAME", "session/fake_news_session"),
    )


def default_channels_from_env() -> list[str]:
    raw = os.getenv("TELEGRAM_DEFAULT_CHANNELS", "")
    return [item.strip() for item in raw.split(",") if item.strip()]


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


async def extract_messages_async(
    config: TelegramConfig,
    channels: Sequence[str],
    *,
    limit: int = 25,
    client_factory: Any = TelegramClient,
) -> list[TelegramMessage]:
    if not channels:
        raise ValueError("Debes indicar al menos un canal o grupo de Telegram.")

    session_path = PROJECT_ROOT / config.session_name
    session_path.parent.mkdir(parents=True, exist_ok=True)

    client = client_factory(str(session_path), config.api_id, config.api_hash)
    messages: list[TelegramMessage] = []

    await client.start()
    try:
        for channel in channels:
            entity = await client.get_entity(channel)
            async for message in client.iter_messages(entity, limit=limit):
                text = _normalize_text(getattr(message, "message", ""))
                if not text:
                    continue

                message_date = getattr(message, "date", None)
                if isinstance(message_date, datetime):
                    if message_date.tzinfo is None:
                        message_date = message_date.replace(tzinfo=timezone.utc)
                    message_date_utc = message_date.astimezone(timezone.utc).isoformat()
                else:
                    message_date_utc = datetime.now(timezone.utc).isoformat()

                messages.append(
                    TelegramMessage(
                        message_id=int(getattr(message, "id", 0)),
                        chat_id=getattr(entity, "id", None),
                        chat_title=getattr(entity, "title", None),
                        channel=channel,
                        sender_id=getattr(message, "sender_id", None),
                        date_utc=message_date_utc,
                        text=text,
                    )
                )
    finally:
        await client.disconnect()

    return messages


def extract_messages(
    config: TelegramConfig,
    channels: Sequence[str],
    *,
    limit: int = 25,
    client_factory: Any = TelegramClient,
) -> list[TelegramMessage]:
    return asyncio.run(extract_messages_async(config, channels, limit=limit, client_factory=client_factory))


def write_messages(messages: Iterable[TelegramMessage], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [message.to_dict() for message in messages]
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
