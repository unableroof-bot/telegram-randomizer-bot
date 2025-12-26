import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

app = FastAPI()

@dp.message()
async def handle_message(message: types.Message):
    if message.text.startswith("/pick"):
        text = message.text.replace("/pick", "").strip()
        if not text:
            await message.answer("Напиши варианты через запятую:\n\n/pick кот, пес, динозавр")
            return

        items = [i.strip() for i in text.split(",") if i.strip()]
        if not items:
            await message.answer("Не вижу вариантов 🤔")
            return

        import random
        choice = random.choice(items)
        await message.answer(f"🎲 Случайный выбор: <b>{choice}</b>")

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
