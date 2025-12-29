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

# Хранилище участников и сообщений для удаления
participants = {}
messages_to_delete = {}

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

    # Новый раунд
    participants[chat_id] = []
    messages_to_delete[chat_id] = []

    sent = await message.answer(
        "Начинаем сбор участников!\n"
        "Нажимайте «🙋 Участвую», чтобы войти в список.",
        reply_markup=pick_menu
    )

    # Сохраняем ID сообщения для удаления
    messages_to_delete[chat_id].append(sent.message_id)


# Нажатие кнопки "Участвую"
@dp.callback_query(lambda c: c.data == "join")
async def join_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = callback.from_user

    if chat_id not in participants:
        participants[chat_id] = []
        messages_to_delete[chat_id] = []

    # Проверка на повтор
    if user.id in [u["id"] for u in participants[chat_id]]:
        await callback.answer("Ты уже участвуешь 😉")
        return

    participants[chat_id].append({"id": user.id, "name": user.full_name})

    sent = await callback.message.answer(
        f"🙋 <b>{user.full_name}</b> участвует!\n"
        f"Всего участников: <b>{len(participants[chat_id])}</b>"
    )

    # Сохраняем ID сообщения
    messages_to_delete[chat_id].append(sent.message_id)

    await callback.answer("Добавил!")


# Нажатие кнопки "Рандомим"
@dp.callback_query(lambda c: c.data == "random")
async def random_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id

    if chat_id not in participants or len(participants[chat_id]) == 0:
        sent = await callback.message.answer("❗ Пока никто не участвует.")
        messages_to_delete[chat_id].append(sent.message_id)
        await callback.answer()
        return

    winner = random.choice(participants[chat_id])
    total = len(participants[chat_id])

    # Удаляем все промежуточные сообщения
    for msg_id in messages_to_delete.get(chat_id, []):
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            pass

    # Очищаем списки
    participants[chat_id] = []
    messages_to_delete[chat_id] = []

    # Итоговое сообщение
    await callback.message.answer(
        f"🎲 Из <b>{total}</b> участников\n"
        f"{winner['name']} оказался в пике своей везучести (или нет)</b>"
    )

    await callback.answer()


# Webhook
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}
