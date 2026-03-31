import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types

# 🔐 ТОКЕН (Railway или вручную)
API_TOKEN = os.getenv("BOT_TOKEN") or "8659770527:AAFU1T-Po7nziaK16hiNPIHFIKgwdl9lC4w"
if not API_TOKEN:
    raise ValueError("Нет токена!")

# 📢 канал
CHANNEL_ID = "@brandpils"

# 👤 разрешённые пользователи (3 аккаунта)
ALLOWED_USERS = [
    1666542263,
    1637194418,
    2028499794
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ▶️ старт
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот работает ✅ Отправь фото или видео")

# 📦 ХРАНИЛИЩЕ АЛЬБОМОВ
media_groups = {}

# 🔥 ОСНОВНОЙ ОБРАБОТЧИК
@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    # 🔒 доступ
    if message.from_user.id not in ALLOWED_USERS:
        return

    # ❗️если это альбом — не обрабатываем тут
    if message.media_group_id:
        return

    text = message.caption or message.text or ""

    # ✨ обработка текста
    items = text.split("\n\n")
    final_text = ""

    for item in items:
        item_text = ""
        lines = item.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 📏 размеры
            if re.search(r'\b(S|M|L|XL)\b', line) or re.search(r'\d{2}\.\d{2}', line):
                item_text += "📏 Размеры: " + line + "\n"
                continue

            # 💰 цена
            if re.search(r'\d+', line):
                clean_price = re.sub(r'[^\d]', '', line)
                if clean_price:
                    line = f"💰 {clean_price}€ (-40%)"

            item_text += line + "\n"

        final_text += item_text + "\n"

    final_text += "🛒 Заказать: https://wa.me/393516282355"

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


# 📦 АЛЬБОМ (НЕСКОЛЬКО ФОТО)
@dp.message_handler(content_types=["photo"], is_media_group=True)
async def handle_album(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    group_id = message.media_group_id

    if not group_id:
        return

    if group_id not in media_groups:
        media_groups[group_id] = []

    media_groups[group_id].append(message)

    # ждём все фото
    await asyncio.sleep(3)

    # если уже обработали
    if group_id not in media_groups:
        return

    messages = media_groups[group_id]

    # если не альбом
    if len(messages) < 2:
        del media_groups[group_id]
        return

    media = []
    text = messages[0].caption or ""

    for i, msg in enumerate(messages):
        if i == 0:
            media.append(types.InputMediaPhoto(
                media=msg.photo[-1].file_id,
                caption=text
            ))
        else:
            media.append(types.InputMediaPhoto(
                media=msg.photo[-1].file_id
            ))

    await bot.send_media_group(CHANNEL_ID, media)

    del media_groups[group_id]


# ▶️ запуск
if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
