import asyncio
from telethon import TelegramClient , events


async def main():
    client = TelegramClient("test session",26685793,"a7b8e912e96416e885da4fdba1800d11")
    @client.on(events.NewMessage)
    async def handle_message(event):
        print(event.message.text)
    await client.start()
    destinatary = await client.get_entity('+34609018698')
    await client.send_message(destinatary,"test message")
    await client.run_until_disconnected()
    return handle_message

asyncio.run(main())
