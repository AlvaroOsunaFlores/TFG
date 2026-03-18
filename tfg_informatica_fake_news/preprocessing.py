from __future__ import annotations

from dataclasses import asdict, dataclass
import html
import re
from typing import Any, Iterable

from langdetect import DetectorFactory, LangDetectException, detect


DetectorFactory.seed = 0

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
MULTISPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ]+", re.IGNORECASE)


@dataclass(frozen=True)
class PreprocessedMessage:
    message_id: int
    channel: str
    language: str
    normalized_text: str
    tokens: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clean_text(text: str) -> str:
    cleaned = html.unescape(str(text or ""))
    cleaned = cleaned.lower()
    cleaned = URL_RE.sub(" url ", cleaned)
    cleaned = MENTION_RE.sub(" usuario ", cleaned)
    cleaned = HASHTAG_RE.sub(r" \1 ", cleaned)
    cleaned = re.sub(r"[^a-z0-9áéíóúüñ\s\.\,\!\?\:\;\(\)\-]", " ", cleaned, flags=re.IGNORECASE)
    cleaned = MULTISPACE_RE.sub(" ", cleaned)
    return cleaned.strip()


def tokenize_text(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def detect_language(text: str) -> str:
    if not text.strip():
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def preprocess_record(record: dict[str, Any]) -> PreprocessedMessage:
    normalized = clean_text(str(record.get("text", "")))
    tokens = tokenize_text(normalized)
    language = detect_language(normalized)
    return PreprocessedMessage(
        message_id=int(record.get("message_id", 0)),
        channel=str(record.get("channel", "")),
        language=language,
        normalized_text=normalized,
        tokens=tokens,
    )


def preprocess_records(records: Iterable[dict[str, Any]]) -> list[PreprocessedMessage]:
    return [preprocess_record(record) for record in records]
