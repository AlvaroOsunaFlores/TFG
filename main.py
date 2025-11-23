import asyncio
import re
import telethon
from telethon import TelegramClient, events
from pymongo import MongoClient
from langdetect import detect
import spacy
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# =============================
#   CONFIG TELEGRAM
# =============================
TELEGRAM_API_ID = 26685793
TELEGRAM_API_HASH = "a7b8e912e96416e885da4fdba1800d11"
PHONE = "+34661899419"

# =============================
#   MODELOS SPACY
# =============================
models = {
    "es": spacy.load("es_core_news_sm"),
    "en": spacy.load("en_core_web_sm"),
    "fr": spacy.load("fr_core_news_sm")
}

# =============================
#   PREPROCESAMIENTO DE TEXTO
# =============================
def preprocesar_texto(msg: str):
    """
    Limpieza y normalización básica del texto.
    - Elimina saltos de línea y espacios extra
    - Convierte a minúsculas
    - Elimina caracteres especiales innecesarios
    """
    msg = re.sub(r'\s+', ' ', msg)  # eliminar saltos de línea y espacios extra
    msg = msg.lower()  # pasar a minúsculas
    msg = re.sub(r'[^a-zA-Z0-9áéíóúñüÁÉÍÓÚÑÜ .,!?¿¡]', '', msg)  # caracteres válidos
    return msg.strip()

# =============================
#   CARGAR MODELO DE AMENAZA
# =============================
MODEL_PATH = "../distilbert_fast_fixed_labels.pt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2
)

# Cargar pesos guardados
state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(state_dict)
model.to(DEVICE)
model.eval()

# =============================
#   ANALISIS DE TEXTO (SPACY) + PREPROCESAMIENTO
# =============================
def analizar_texto(msg: str):
    try:
        # 1️⃣ Preprocesamiento
        msg_limpio = preprocesar_texto(msg)

        # 2️⃣ Detección de idioma
        lang = detect(msg_limpio)
        print(f"Idioma detectado: {lang}")

        if lang not in models:
            print(f"No hay modelo para '{lang}', usando español por defecto.")
            lang = "es"

        # 3️⃣ Procesamiento con spaCy
        nlp = models[lang]
        doc = nlp(msg_limpio)
        tokens = [token.text for token in doc]
        lemas = [token.lemma_ for token in doc]
        entidades = [(ent.text, ent.label_) for ent in doc.ents]

        return msg_limpio, tokens, lemas, entidades, lang

    except Exception as e:
        print("Error en análisis de texto:", e)
        return msg, [], [], [], "desconocido"

# =============================
#   CLASIFICAR AMENAZA (IA)
# =============================
def clasificar_mensaje(msg: str):
    # Preprocesar antes de tokenizar para IA
    msg_limpio = preprocesar_texto(msg)
    inputs = tokenizer(msg_limpio, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)
        prob = probs[0, 1].item()  # Probabilidad de la clase "amenaza"

    # Clasificación usando umbrales
    if prob < 0.54:
        clase = "seguro"
    elif 0.54 <= prob <= 0.75:
        clase = "incertidumbre"
    elif prob > 0.75:
        clase = "amenaza"
    else:
        clase = "sin_definir"

    return prob, clase

# =============================
#   MAIN ASYNC TELEGRAM
# =============================
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

        # Preprocesamiento + spaCy
        msg_limpio, tokens, lemas, entidades, lang = analizar_texto(msg)

        # Clasificación IA
        try:
            score, clase = clasificar_mensaje(msg)
        except Exception as e:
            print(f"Error en clasificación de mensaje: {e}")
            score, clase = None, "error"

        # Guardar en DB
        instdb = {
            "_id": idCount,
            "user_id": usr,
            "msg_original": msg,
            "msg_limpio": msg_limpio,
            "idioma": lang,
            "tokens": tokens,
            "lemas": lemas,
            "entidades": entidades,
            "amenaza_score": score,
            "tipo": clase
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
