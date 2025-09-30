import telethon
import pymongo
import asyncio

from pymongo import MongoClient
from telethon import TelegramClient, events

TELEGRAM_API_ID = 26685793
TELEGRAM_API_HASH = "a7b8e912e96416e885da4fdba1800d11"

async def main():
    idCount = 0
    client = TelegramClient("study_Session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    clientdb = MongoClient('localhost', 27017)
    db = clientdb['Testq']
    collection = db['CollectionTest']
    collection.delete_many({})

    await client.start()
    @client.on(events.NewMessage)
    async def msgHandler(event):
        nonlocal idCount
        msg = event.message.text
        usr = event.message.sender_id

        instdb = {"_id": idCount, "user_id": usr,"msg": msg }
        try:
            collection.insert_one(instdb)
            print(f"Guardado en DB: {instdb}")
        except Exception as e:
            print("Error al guardar en MongoDB:", e)

        idCount += 1
    await client.run_until_disconnected()
    return
asyncio.run(main())
