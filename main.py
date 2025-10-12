import asyncio
import telethon
from pymongo import MongoClient
from telethon import TelegramClient, events
from langdetect import detect
import spacy


TELEGRAM_API_ID = 26685793
TELEGRAM_API_HASH = "a7b8e912e96416e885da4fdba1800d11"
PHONE = "+34661899419"


models = {
    "es": spacy.load("es_core_news_sm"),
    "en": spacy.load("en_core_web_sm"),
    "fr": spacy.load("fr_core_news_sm")
}

def analizar_texto(msg: str):

    try:
        lang = detect(msg)
        print(f"Idioma detectado: {lang}")

        if lang not in models:
            print(f"No hay modelo para '{lang}', usando español por defecto.")
            lang = "es"

        nlp = models[lang]
        doc = nlp(msg)
        tokens = [token.text for token in doc]
        lemas = [token.lemma_ for token in doc]
        entidades = [(ent.text, ent.label_) for ent in doc.ents]

        return tokens, lemas, entidades, lang

    except Exception as e:
        print("Error en análisis de texto:", e)
        return [], [], [], "desconocido"

async def main():
    idCount = 0
    client = TelegramClient("study_Session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    clientdb = MongoClient('localhost', 27017)
    db = clientdb['Testq']
    collection = db['CollectionTest']
    collection.delete_many({})


    await client.connect()
    if not await client.is_user_authorized():
        print("No autorizado. Enviando código a Telegram...")
        await client.send_code_request(PHONE)
        code = input("Introduce el código que te envió Telegram: ")

        try:
            await client.sign_in(PHONE, code)
        except telethon.errors.SessionPasswordNeededError:
            password = input("Tu cuenta tiene verificación en dos pasos. Introduce tu contraseña: ")
            await client.sign_in(password=password)

    print("Sesión iniciada correctamente.")
    me = await client.get_me()
    print(f"Conectado como {me.first_name} (@{me.username})")

    @client.on(events.NewMessage)
    async def msgHandler(event):
        nonlocal idCount
        msg = event.message.text or ""
        usr = event.message.sender_id

        if not msg.strip():
            return

        tokens, lemas, entidades, lang = analizar_texto(msg)

        instdb = {
            "_id": idCount,
            "user_id": usr,
            "msg": msg,
            "idioma": lang,
            "tokens": tokens,
            "lemas": lemas,
            "entidades": entidades
        }

        try:
            collection.insert_one(instdb)
            print(f"Guardado en DB: {instdb}")
        except Exception as e:
            print("Error al guardar en DB:", e)

        idCount += 1

    print("Escuchando mensajes:")
    await client.run_until_disconnected()

asyncio.run(main())


