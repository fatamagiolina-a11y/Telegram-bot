import re
import os
import asyncio
from aiogram import Bot, Dispatcher, types

# 🔐 токен (Railway + запасной вариант)
API_TOKEN = os.getenv("BOT_TOKEN") or "8659770527:AAFU1T-Po7nziaK16hiNPIHFIKgwdl9lC4w"

if not API_TOKEN:
    raise ValueError("Нет токена!")

CHANNEL_ID = "@brandpils"

# 👤 разрешённые пользователи (3 аккаунта)
ALLOWED_USERS = [
    1666542263,   # твой основной (оставь свой)
    1637194418,
    2028499794
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# ▶️ команда старт
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот работает ✅ Отправь фото или видео")


# 🚀 основной обработчик
@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    # 🔒 проверка доступа
    if message.from_user.id not in ALLOWED_USERS:
        return

    text = message.caption or message.text or ""

    items = text.split("\n\n")
    final_text = ""

    for item in items:
        item_text = ""
        lines = item.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 📏 размеры (без дублей)
            if re.search(r'\b(S|M|L|XL)\b', line) or re.search(r'\d{2}\.\d{2}', line):
                item_text += "📏 Размеры: " + line + "\n"
                continue

            # 💸 цена
            if re.search(r'\d+', line):
                clean_price = re.sub(r'[^\d]', '', line)
                if clean_price:
                    line = f"💸 {clean_price}€ (-40%)"

            item_text += line + "\n"

        final_text += item_text + "\n"

    final_text += "📲 Заказать: https://wa.me/393516282355"

    try:
        if message.video:
            await bot.send_video(
                CHANNEL_ID,
                message.video.file_id,
                caption=final_text
            )

        elif message.photo:
            await bot.send_photo(
                CHANNEL_ID,
                message.photo[-1].file_id,
                caption=final_text
            )

        else:
            await bot.send_message(
                CHANNEL_ID,
                final_text
            )

    except Exception as e:
        print("ERROR:", e)
from aiogram.types import MediaGroup

media_groups = {}


@dp.message_handler(content_types=["photo"])
async def handle_album(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    group_id = message.media_group_id

    if group_id not in media_groups:
        media_groups[group_id] = []

    media_groups[group_id].append(message)

    await asyncio.sleep(1)

    if len(media_groups[group_id]) == 1:
        return

    messages = media_groups[group_id]
    media = []

    text = messages[0].caption or ""

    for i, msg in enumerate(messages):
        if i == 0:
            media.append(types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=text))
        else:
            media.append(types.InputMediaPhoto(media=msg.photo[-1].file_id))

    await bot.send_media_group(CHANNEL_ID, media)

    del media_groups[group_id]

if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
