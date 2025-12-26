import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

app = FastAPI()

# --- Меню ---
inline_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Случайный выбор", callback_data="pick")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ]
)

# --- Команда /start ---
@dp.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Выбери действие:", reply_markup=inline_menu)

# --- Обработка кнопок ---
@dp.callback_query(lambda c: c.data == "pick")
async def process_pick(callback: types.CallbackQuery):
    await callback.message.answer("Напиши варианты через запятую:\n/pick кот, пес, динозавр")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "help")
async def process_help(callback: types.CallbackQuery):
    await callback.message.answer("Это бот для случайного выбора.\nИспользуй команду:\n/pick кот, пес, динозавр")
    await callback.answer()

# --- Обработка /pick ---
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

# --- Webhook ---
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
