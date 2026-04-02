from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import time
import uuid

from dotenv import load_dotenv
from langdetect import detect
from pymongo import ASCENDING, DESCENDING
import torch

from model_loader import load_tokenizer_and_model
from privacy_utils import env_flag, pseudonymize_identifier


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)


@dataclass(frozen=True)
class PipelineSettings:
    hf_model: str
    threshold: float
    pii_salt: str
    store_msg_original: bool
    store_msg_normalized: bool
    store_nlp_features: bool
    retention_days: int


def load_pipeline_settings() -> PipelineSettings:
    return PipelineSettings(
        hf_model=os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels"),
        threshold=float(os.getenv("THRESHOLD", "0.05")),
        pii_salt=os.getenv("PII_SALT", "change-me-local-salt"),
        store_msg_original=env_flag(os.getenv("STORE_MSG_ORIGINAL"), default=False),
        store_msg_normalized=env_flag(os.getenv("STORE_MSG_NORMALIZED"), default=False),
        store_nlp_features=env_flag(os.getenv("STORE_NLP_FEATURES"), default=False),
        retention_days=int(os.getenv("RETENTION_DAYS", "30")),
    )


def generate_run_id() -> str:
    return os.getenv("RUN_ID", str(uuid.uuid4()))


def iso_now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def milliseconds_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return round((end - start).total_seconds() * 1000, 3)


def preprocesar_texto(msg: str) -> str:
    msg = re.sub(r"\s+", " ", str(msg))
    msg = msg.lower()
    msg = re.sub(r"[^a-zA-Z0-9\u00C0-\u017F .,!?\u00BF\u00A1:/_-]", "", msg)
    return msg.strip()


def analizar_texto(msg: str) -> tuple[str, str, list[str], float]:
    started = time.perf_counter()
    msg_limpio = preprocesar_texto(msg)

    if not msg_limpio:
        return msg_limpio, "desconocido", [], round((time.perf_counter() - started) * 1000, 3)

    try:
        lang = detect(msg_limpio)
    except Exception:
        lang = "desconocido"

    tokens = msg_limpio.split()
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    return msg_limpio, lang, tokens, latency_ms


@dataclass
class InferenceResult:
    pred: int
    score_1: float
    inference_latency_ms: float


class InferencePipeline:
    def __init__(self, settings: PipelineSettings) -> None:
        self.settings = settings
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer, self.model, self.model_source = load_tokenizer_and_model(settings.hf_model, self.device)

    def infer(self, msg_limpio: str) -> InferenceResult:
        started = time.perf_counter()
        text = msg_limpio or "mensaje vacio"
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=1)[0].tolist()

        score_1 = float(probs[1])
        pred = 1 if score_1 >= self.settings.threshold else 0
        inference_latency_ms = round((time.perf_counter() - started) * 1000, 3)
        return InferenceResult(pred=pred, score_1=score_1, inference_latency_ms=inference_latency_ms)


def ensure_indexes(collection, retention_days: int) -> None:
    collection.create_index([("run_id", ASCENDING)], name="run_id_idx")
    collection.create_index([("msg_sha256", ASCENDING)], name="msg_sha256_idx")
    collection.create_index([("created_at_utc", DESCENDING)], name="created_at_utc_idx")
    collection.create_index([("source_received_at_utc", DESCENDING)], name="source_received_at_utc_idx")
    collection.create_index(
        [("created_at_utc", ASCENDING)],
        name="created_at_utc_ttl_idx",
        expireAfterSeconds=max(retention_days, 1) * 86400,
    )


def build_queue_payload(
    *,
    text: str,
    sender_id: str | int | None,
    chat_id: str | int | None,
    message_id: int | None,
    channel: str | None,
    run_id: str,
    source: str,
    source_received_at_utc: str | None = None,
) -> dict[str, object]:
    queued_at_utc = iso_now_utc()
    return {
        "run_id": run_id,
        "text": text,
        "sender_id": sender_id,
        "chat_id": chat_id,
        "message_id": message_id,
        "channel": channel,
        "source": source,
        "source_received_at_utc": source_received_at_utc or queued_at_utc,
        "queued_at_utc": queued_at_utc,
    }


def build_message_document(
    payload: dict[str, object],
    *,
    pipeline: InferencePipeline,
    settings: PipelineSettings,
    resource_snapshot: dict[str, float | int | None] | None = None,
    queue_depth: int | None = None,
) -> dict[str, object]:
    msg = str(payload.get("text", "") or "")
    created_at = datetime.now(timezone.utc)
    queued_at = parse_iso_datetime(str(payload.get("queued_at_utc") or "")) or created_at
    source_received_at = parse_iso_datetime(str(payload.get("source_received_at_utc") or "")) or queued_at

    msg_limpio, lang, tokens, preprocess_latency_ms = analizar_texto(msg)

    error: str | None = None
    pred: int | None = None
    score_1: float | None = None
    inference_latency_ms: float | None = None

    try:
        inference = pipeline.infer(msg_limpio)
        pred = inference.pred
        score_1 = inference.score_1
        inference_latency_ms = inference.inference_latency_ms
    except Exception as exc:
        error = str(exc)

    queue_wait_latency_ms = milliseconds_between(source_received_at, queued_at)
    end_to_end_latency_ms = milliseconds_between(source_received_at, created_at)

    user_hash = pseudonymize_identifier(payload.get("sender_id"), namespace="user_id", salt=settings.pii_salt)
    chat_hash = pseudonymize_identifier(payload.get("chat_id"), namespace="chat_id", salt=settings.pii_salt)

    document: dict[str, object] = {
        "run_id": str(payload.get("run_id") or generate_run_id()),
        "created_at_utc": created_at,
        "persisted_at_utc": None,
        "source_received_at_utc": source_received_at,
        "queued_at_utc": queued_at,
        "source": str(payload.get("source") or "unknown"),
        "channel": payload.get("channel"),
        "user_hash": user_hash,
        "chat_hash": chat_hash,
        "message_id": payload.get("message_id"),
        "msg_sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(),
        "idioma": lang,
        "pred": pred,
        "score_1": score_1,
        "latency_ms": inference_latency_ms,
        "preprocess_latency_ms": preprocess_latency_ms,
        "inference_latency_ms": inference_latency_ms,
        "db_write_latency_ms": None,
        "queue_wait_latency_ms": queue_wait_latency_ms,
        "end_to_end_latency_ms": end_to_end_latency_ms,
        "threshold": settings.threshold,
        "hf_model": settings.hf_model,
        "model_source": pipeline.model_source,
        "device": str(pipeline.device),
        "ok": error is None,
        "error": error,
        "queue_depth": queue_depth,
    }

    if resource_snapshot:
        document.update(resource_snapshot)

    if settings.store_msg_original:
        document["msg_original"] = msg
    if settings.store_msg_normalized:
        document["msg_limpio"] = msg_limpio
    if settings.store_nlp_features:
        document["tokens"] = tokens

    return document


def finalize_persisted_document(document: dict[str, object], db_write_latency_ms: float) -> dict[str, object]:
    persisted_at = datetime.now(timezone.utc)
    updated = dict(document)
    updated["persisted_at_utc"] = persisted_at
    updated["db_write_latency_ms"] = round(db_write_latency_ms, 3)

    source_received_at = updated.get("source_received_at_utc")
    if isinstance(source_received_at, datetime):
        total_latency_ms = milliseconds_between(source_received_at, persisted_at)
        updated["end_to_end_latency_ms"] = total_latency_ms

    return updated
