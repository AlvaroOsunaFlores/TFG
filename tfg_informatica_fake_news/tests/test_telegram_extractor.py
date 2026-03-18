from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from telegram_extractor import TelegramConfig, extract_messages


@dataclass
class _FakeMessage:
    id: int
    message: str
    sender_id: int
    date: datetime


@dataclass
class _FakeEntity:
    id: int
    title: str


class _FakeClient:
    def __init__(self, session_name: str, api_id: int, api_hash: str) -> None:
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.connected = False

    async def start(self) -> None:
        self.connected = True

    async def get_entity(self, channel: str) -> _FakeEntity:
        return _FakeEntity(id=-1000, title=f"Entity {channel}")

    async def iter_messages(self, entity: _FakeEntity, limit: int):
        sample = [
            _FakeMessage(1, "Primer mensaje", 11, datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc)),
            _FakeMessage(2, "Segundo mensaje", 12, datetime(2026, 3, 18, 10, 0, tzinfo=timezone.utc)),
        ]
        for item in sample[:limit]:
            yield item

    async def disconnect(self) -> None:
        self.connected = False


def test_extract_messages_returns_structured_messages() -> None:
    config = TelegramConfig(api_id=1, api_hash="hash", session_name="session/test")
    messages = extract_messages(config, ["canal-demo"], limit=2, client_factory=_FakeClient)

    assert len(messages) == 2
    assert messages[0].channel == "canal-demo"
    assert messages[0].chat_title == "Entity canal-demo"
    assert messages[0].date_utc.endswith("+00:00")


def test_extract_messages_requires_channels() -> None:
    config = TelegramConfig(api_id=1, api_hash="hash", session_name="session/test")
    try:
        extract_messages(config, [], client_factory=_FakeClient)
    except ValueError as exc:
        assert "al menos un canal" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError si no hay canales")
