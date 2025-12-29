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

# Хранилище участников (по чатам)
participants = {}

# Кнопки
pick_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🙋 Участвую", callback_data="join")],
        [InlineKeyboardButton(text="🎲 Рандомим", callback_data="random")]
    ]
)

# Команда /pick
@dp.message(Command("pick"))
async def pick_command(message: types.Message):
    chat_id = message.chat.id
    participants[chat_id] = []  # очищаем список для нового раунда
    await message.answer("Начинаем сбор участников!", reply_markup=pick_menu)

# Нажатие кнопки "Участвую"
@dp.callback_query(lambda c: c.data == "join")
async def join_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    # создаём список, если его нет
    if chat_id not in participants:
        participants[chat_id] = []

    # проверяем, не добавлен ли уже
    if user.id not in [u["id"] for u in participants[chat_id]]:
        participants[chat_id].append({"id": user.id, "name": user.full_name})
        await callback.answer("Ты участвуешь!")
    else:
        await callback.answer("Ты уже в списке", show_alert=False)

# Нажатие кнопки "Рандомим"
@dp.callback_query(lambda c: c.data == "random")
async def random_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in participants or len(participants[chat_id]) == 0:
        await callback.answer("Пока никто не участвует!", show_alert=True)
        return

    winner = random.choice(participants[chat_id])
    participants[chat_id] = []  # очищаем список после выбора

    await callback.message.answer(f"🎉 Победитель: <b>{winner['name']}</b>")
    await callback.answer()

# Webhook
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
