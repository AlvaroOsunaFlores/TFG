from __future__ import annotations

from dataclasses import asdict, dataclass
import html
import os
import re
from typing import Any, Iterable

from langdetect import DetectorFactory, LangDetectException, detect


DetectorFactory.seed = 0

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
EMOJI_RE = re.compile(r"[\U00010000-\U0010ffff]", re.UNICODE)
MULTISPACE_RE = re.compile(r"\s+")
LATIN_TEXT_CLASS = "a-z0-9\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1"
TOKEN_RE = re.compile(rf"[{LATIN_TEXT_CLASS}]+", re.IGNORECASE)
DEFAULT_STOPWORDS = {"de", "la", "el", "y", "a"}


@dataclass(frozen=True)
class PreprocessedMessage:
    message_id: int
    channel: str
    language: str
    normalized_text: str
    tokens: list[str]
    token_count: int
    quality_flags: list[str]
    is_usable: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_stopwords() -> set[str]:
    raw = os.getenv("PREPROCESS_STOPWORDS", "").strip()
    if not raw:
        return set(DEFAULT_STOPWORDS)
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def clean_text(text: str) -> str:
    cleaned = html.unescape(str(text or ""))
    cleaned = cleaned.lower()
    cleaned = URL_RE.sub(" url ", cleaned)
    cleaned = MENTION_RE.sub(" usuario ", cleaned)
    cleaned = HASHTAG_RE.sub(r" \1 ", cleaned)
    cleaned = EMOJI_RE.sub(" ", cleaned)
    cleaned = re.sub(
        rf"[^{LATIN_TEXT_CLASS}\s\.\,\!\?\:\;\(\)\-]",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
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
    filtered_tokens = [token for token in tokens if token not in load_stopwords()]
    language = detect_language(normalized)

    min_tokens = int(os.getenv("PREPROCESS_MIN_TOKENS", "3"))
    quality_flags: list[str] = []
    if not normalized:
        quality_flags.append("empty_text")
    if len(filtered_tokens) < min_tokens:
        quality_flags.append("too_short")
    if language == "unknown":
        quality_flags.append("unknown_language")

    normalized_text = " ".join(filtered_tokens) if filtered_tokens else normalized
    return PreprocessedMessage(
        message_id=int(record.get("message_id", 0)),
        channel=str(record.get("channel", "")),
        language=language,
        normalized_text=normalized_text,
        tokens=filtered_tokens,
        token_count=len(filtered_tokens),
        quality_flags=quality_flags,
        is_usable="too_short" not in quality_flags and "empty_text" not in quality_flags,
    )


def preprocess_records(records: Iterable[dict[str, Any]]) -> list[PreprocessedMessage]:
    return [preprocess_record(record) for record in records]
