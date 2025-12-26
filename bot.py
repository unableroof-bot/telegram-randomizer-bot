import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram import F
import asyncio

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в переменных окружения")

from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

@dp.message(F.text.startswith("/pick"))
async def pick_handler(message: types.Message):
    text = message.text.replace("/pick", "").strip()
    if not text:
        await message.answer("Напиши варианты через запятую:\n\n<i>/pick вариант1, вариант2, вариант3</i>")
        return

    items = [i.strip() for i in text.split(",") if i.strip()]
    if not items:
        await message.answer("Не вижу вариантов после команды 🤔")
        return

    choice = random.choice(items)
    await message.answer(f"🎲 Случайный выбор: <b>{choice}</b>")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
