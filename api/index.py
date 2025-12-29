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
    participants[chat_id] = []  # новый раунд
    await message.answer(
        "Начинаем сбор участников!\n\n"
        "Нажимай кнопку <b>«🙋 Участвую»</b>, чтобы войти в список.\n"
        "Когда будете готовы — жмите <b>«🎲 Рандомим»</b>.",
        reply_markup=pick_menu
    )

# Нажатие кнопки "Участвую"
@dp.callback_query(lambda c: c.data == "join")
async def join_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in participants:
        participants[chat_id] = []

    # уже участвует?
    if user.id in [u["id"] for u in participants[chat_id]]:
        await callback.answer("Ты уже участвуешь 😉", show_alert=False)
        return

    participants[chat_id].append({"id": user.id, "name": user.full_name})

    count = len(participants[chat_id])
    # сообщение в чат, чтобы было видно, что кто-то добавился
    await callback.message.answer(
        f"🙋 <b>{user.full_name}</b> участвует!\n"
        f"Сейчас в списке: <b>{count}</b> участник(ов)."
    )

    await callback.answer("Добавил в список!")

# Нажатие кнопки "Рандомим"
@dp.callback_query(lambda c: c.data == "random")
async def random_handler(callback: Types.CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in participants or len(participants[chat_id]) == 0:
        await callback.message.answer("❗ Пока никто не участвует.\nСначала нажмите «🙋 Участвую».")
        await callback.answer("Список пуст", show_alert=False)
        return

    # выбираем победителя
    winner = random.choice(participants[chat_id])
    total = len(participants[chat_id])

    participants[chat_id] = []  # очищаем список после рандома

    await callback.message.answer(
        f"🎲 Разыгрывали между <b>{total}</b> участниками.\n"
        f"🎉 Победитель: <b>{winner['name']}</b>"
    )
    await callback.answer("Готово!")
    
# Webhook
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
