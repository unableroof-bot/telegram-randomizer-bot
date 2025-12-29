import os
import random
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = FastAPI()

participants = {}

pick_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🙋 Участвую", callback_data="join")],
        [InlineKeyboardButton(text="🎲 Рандомим", callback_data="random")]
    ]
)

@dp.message(Command("pick"))
async def pick_command(message: types.Message):
    chat_id = message.chat.id
    participants[chat_id] = []
    await message.answer("Начинаем сбор участников!", reply_markup=pick_menu)

@dp.callback_query(lambda c: c.data == "join")
async def join_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in participants:
        participants[chat_id] = []

    if user.id in [u["id"] for u in participants[chat_id]]:
        await callback.answer("Ты уже участвуешь 😉")
        return

    participants[chat_id].append({"id": user.id, "name": user.full_name})
    await callback.message.answer(f"🙋 {user.full_name} участвует!")
    await callback.answer("Добавил!")

@dp.callback_query(lambda c: c.data == "random")
async def random_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in participants or len(participants[chat_id]) == 0:
        await callback.message.answer("❗ Пока никто не участвует.")
        await callback.answer()
        return

    winner = random.choice(participants[chat_id])
    participants[chat_id] = []

    await callback.message.answer(f"🎉 Победитель: <b>{winner['name']}</b>")
    await callback.answer()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
