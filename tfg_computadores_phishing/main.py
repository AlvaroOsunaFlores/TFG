from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import time
import uuid

from dotenv import load_dotenv
from langdetect import detect
from pymongo import ASCENDING, DESCENDING, MongoClient
from telethon import TelegramClient, events
import telethon
import torch

from model_loader import load_tokenizer_and_model
from privacy_utils import env_flag, pseudonymize_identifier


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH if ENV_PATH.exists() else None)

_api_id = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

if not _api_id:
    raise ValueError("Falta TELEGRAM_API_ID en el .env")
if not TELEGRAM_API_HASH:
    raise ValueError("Falta TELEGRAM_API_HASH en el .env")
if not PHONE:
    raise ValueError("Falta TELEGRAM_PHONE en el .env (formato recomendado: +34XXXXXXXXX)")

TELEGRAM_API_ID = int(_api_id)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
MONGO_DB = os.getenv("MONGO_DB", "tfg")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "messages")
HF_MODEL = os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels")
THRESHOLD = float(os.getenv("THRESHOLD", "0.05"))
RUN_ID = os.getenv("RUN_ID", str(uuid.uuid4()))
PII_SALT = os.getenv("PII_SALT", "change-me-local-salt")
STORE_MSG_ORIGINAL = env_flag(os.getenv("STORE_MSG_ORIGINAL"), default=False)
STORE_MSG_NORMALIZED = env_flag(os.getenv("STORE_MSG_NORMALIZED"), default=False)
STORE_NLP_FEATURES = env_flag(os.getenv("STORE_NLP_FEATURES"), default=False)
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Cargando modelo desde HuggingFace...")
tokenizer, model, MODEL_SOURCE = load_tokenizer_and_model(HF_MODEL, DEVICE)
print(f"Modelo cargado correctamente. source={MODEL_SOURCE}")


def preprocesar_texto(msg: str) -> str:
    msg = re.sub(r"\s+", " ", msg)
    msg = msg.lower()
    msg = re.sub(r"[^a-zA-Z0-9\u00C0-\u017F .,!?\u00BF\u00A1]", "", msg)
    return msg.strip()


def analizar_texto(msg: str) -> tuple[str, str]:
    msg_limpio = preprocesar_texto(msg)
    if not msg_limpio:
        return msg_limpio, "desconocido"

    try:
        lang = detect(msg_limpio)
    except Exception:
        lang = "desconocido"
    return msg_limpio, lang


def clasificar_binario(msg: str) -> tuple[int, float, float]:
    msg_limpio = preprocesar_texto(msg)

    t0 = time.perf_counter()
    inputs = tokenizer(msg_limpio, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(DEVICE) for key, value in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0].tolist()

    p1 = float(probs[1])
    pred = 1 if p1 >= THRESHOLD else 0
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    return pred, p1, latency_ms


def ensure_indexes(collection) -> None:
    collection.create_index([("run_id", ASCENDING)], name="run_id_idx")
    collection.create_index([("msg_sha256", ASCENDING)], name="msg_sha256_idx")
    collection.create_index([("created_at_utc", DESCENDING)], name="created_at_utc_idx")
    collection.create_index(
        [("created_at_utc", ASCENDING)],
        name="created_at_utc_ttl_idx",
        expireAfterSeconds=max(RETENTION_DAYS, 1) * 86400,
    )


def build_message_document(event, msg: str, msg_limpio: str, lang: str) -> dict[str, object]:
    user_hash = pseudonymize_identifier(event.message.sender_id, namespace="user_id", salt=PII_SALT)
    chat_hash = pseudonymize_identifier(event.chat_id, namespace="chat_id", salt=PII_SALT)

    try:
        pred, score_1, latency_ms = clasificar_binario(msg)
        error = None
    except Exception as exc:
        pred, score_1, latency_ms = None, None, None
        error = str(exc)

    payload: dict[str, object] = {
        "run_id": RUN_ID,
        "created_at_utc": datetime.now(timezone.utc),
        "user_hash": user_hash,
        "chat_hash": chat_hash,
        "message_id": event.message.id,
        "msg_sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(),
        "idioma": lang,
        "pred": pred,
        "score_1": score_1,
        "latency_ms": latency_ms,
        "ok": error is None,
        "error": error,
        "threshold": THRESHOLD,
        "hf_model": HF_MODEL,
        "model_source": MODEL_SOURCE,
        "device": str(DEVICE),
    }

    if STORE_MSG_ORIGINAL:
        payload["msg_original"] = msg
    if STORE_MSG_NORMALIZED:
        payload["msg_limpio"] = msg_limpio
    if STORE_NLP_FEATURES:
        payload["tokens"] = msg_limpio.split()

    return payload


async def main() -> None:
    session_path = PROJECT_ROOT / "session" / "study_Session"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    client = TelegramClient(str(session_path), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    mongo = MongoClient(MONGO_URI)
    collection = mongo[MONGO_DB][MONGO_COLLECTION]
    ensure_indexes(collection)

    await client.connect()

    if not await client.is_user_authorized():
        print("Enviando codigo...")
        await client.send_code_request(PHONE)
        code = input("Introduce el codigo enviado por Telegram: ")

        try:
            await client.sign_in(PHONE, code)
        except telethon.errors.SessionPasswordNeededError:
            password = input("Introduce tu password de 2FA: ")
            await client.sign_in(password=password)

        print("Sesion iniciada correctamente.")

    me = await client.get_me()
    username = getattr(me, "username", None)
    print(f"Conectado como {me.first_name} (@{username})")
    print(f"RUN_ID={RUN_ID}")
    print(
        "Privacidad -> "
        f"msg_original={STORE_MSG_ORIGINAL}, msg_limpio={STORE_MSG_NORMALIZED}, "
        f"tokens={STORE_NLP_FEATURES}, retention_days={RETENTION_DAYS}"
    )

    @client.on(events.NewMessage)
    async def handler(event) -> None:
        msg = event.message.text or ""
        if not msg.strip():
            return

        msg_limpio, lang = analizar_texto(msg)
        document = build_message_document(event, msg, msg_limpio, lang)

        try:
            collection.insert_one(document)
            print(
                "Guardado -> "
                f"message_id={event.message.id}, pred={document.get('pred')}, "
                f"score_1={document.get('score_1')}, latency_ms={document.get('latency_ms')}"
            )
        except Exception as exc:
            print("Error al guardar:", exc)

    print("Bot escuchando mensajes...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
