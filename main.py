import asyncio
import os
import re
import time
import uuid
import hashlib
from datetime import datetime, timezone

from dotenv import load_dotenv
from langdetect import detect
from pymongo import MongoClient
from telethon import TelegramClient, events
import telethon

import spacy
import torch
from model_loader import load_tokenizer_and_model


load_dotenv()

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
HF_MODEL = os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels")
THRESHOLD = float(os.getenv("THRESHOLD", "0.05"))
RUN_ID = os.getenv("RUN_ID", str(uuid.uuid4()))


models = {
    "es": spacy.load("es_core_news_sm"),
    "en": spacy.load("en_core_web_sm"),
    "fr": spacy.load("fr_core_news_sm"),
}


def preprocesar_texto(msg: str) -> str:
    msg = re.sub(r"\s+", " ", msg)
    msg = msg.lower()
    msg = re.sub(r"[^a-zA-Z0-9\u00C0-\u017F .,!?\u00BF\u00A1]", "", msg)
    return msg.strip()


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Cargando modelo desde HuggingFace...")
tokenizer, model, MODEL_SOURCE = load_tokenizer_and_model(HF_MODEL, DEVICE)
print(f"Modelo cargado correctamente. source={MODEL_SOURCE}")


def analizar_texto(msg: str):
    try:
        msg_limpio = preprocesar_texto(msg)
        lang = detect(msg_limpio)
        if lang not in models:
            lang = "es"

        nlp = models[lang]
        doc = nlp(msg_limpio)

        tokens = [token.text for token in doc]
        lemas = [token.lemma_ for token in doc]
        entidades = [(ent.text, ent.label_) for ent in doc.ents]

        return msg_limpio, tokens, lemas, entidades, lang
    except Exception:
        return msg, [], [], [], "desconocido"


def clasificar_binario(msg: str):
    msg_limpio = preprocesar_texto(msg)

    t0 = time.perf_counter()
    inputs = tokenizer(msg_limpio, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0].tolist()

    # Clase 1 = amenaza
    p1 = float(probs[1])
    pred = 1 if p1 >= THRESHOLD else 0
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)
    return pred, p1, latency_ms


async def main():
    client = TelegramClient("session/study_Session", TELEGRAM_API_ID, TELEGRAM_API_HASH)

    mongo = MongoClient(MONGO_URI)
    db = mongo["tfg"]
    collection = db["messages"]

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

    @client.on(events.NewMessage)
    async def handler(event):
        msg = event.message.text or ""
        usr = event.message.sender_id

        if not msg.strip():
            return

        msg_limpio, tokens, lemas, entidades, lang = analizar_texto(msg)
        error = None

        try:
            pred, score_1, latency_ms = clasificar_binario(msg)
        except Exception as e:
            pred, score_1, latency_ms = None, None, None
            error = str(e)

        instdb = {
            "run_id": RUN_ID,
            "created_at_utc": datetime.now(timezone.utc),
            "user_id": usr,
            "chat_id": event.chat_id,
            "message_id": event.message.id,
            "msg_original": msg,
            "msg_limpio": msg_limpio,
            "msg_sha256": hashlib.sha256(msg.encode("utf-8")).hexdigest(),
            "idioma": lang,
            "tokens": tokens,
            "lemas": lemas,
            "entidades": entidades,
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

        try:
            collection.insert_one(instdb)
            print(
                "Guardado -> "
                f"chat_id={event.chat_id}, message_id={event.message.id}, pred={pred}, score_1={score_1}, latency_ms={latency_ms}"
            )
        except Exception as e:
            print("Error al guardar:", e)

    print("Bot escuchando mensajes...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
