import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types

API_TOKEN = "8659770527:AAFU1T-Po7nziaK16hiNPIHFIKgwdl9lC4w"

CHANNEL_ID = "@brandpils"

ALLOWED_USERS = [
    1666542263,
    1637194418,
    2028499794
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

media_groups = {}

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот работает ✅ Отправь фото или видео")

def process_text(text):
    items = text.split("\n\n")
    final_text = ""

    for item in items:
        item_text = ""
        lines = item.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.search(r'\b(S|M|L|XL)\b', line) or re.search(r'\d{2}\.\d{2}', line):
                item_text += "📏 Размеры: " + line + "\n"
                continue

            if re.search(r'\d+', line):
                clean_price = re.sub(r'[^\d]', '', line)
                if clean_price:
                    line = f"💰 {clean_price}€ (-40%)"

            item_text += line + "\n"

        final_text += item_text + "\n"

    final_text += "🛒 Заказать: https://wa.me/393516282355"
    return final_text


@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    # --- АЛЬБОМ ---
    if message.media_group_id:
        group_id = message.media_group_id

        # если уже обработан — выходим
        if group_id not in media_groups:
            media_groups[group_id] = []

        media_groups[group_id].append(message)

        await asyncio.sleep(2)

        messages = media_groups.get(group_id)

        # если уже удалили — не повторяем
        if not messages:
            return

        if len(messages) < 2:
            return

        # 🔥 ОБРАБАТЫВАЕМ ТОЛЬКО 1 РАЗ
        if message != messages[-1]:
            return

        media = []

        text = ""
        for msg in messages:
            if msg.caption:
                text = msg.caption
                break

        final_text = process_text(text)

        for i, msg in enumerate(messages):
            if i == 0:
                media.append(types.InputMediaPhoto(
                    media=msg.photo[-1].file_id,
                    caption=final_text
                ))
            else:
                media.append(types.InputMediaPhoto(
                    media=msg.photo[-1].file_id
                ))

        await bot.send_media_group(CHANNEL_ID, media)

        # 🔥 удаляем безопасно
        media_groups.pop(group_id, None)
        return

    # --- ОДИНОЧНЫЙ ПОСТ ---
    text = message.caption or message.text or ""
    final_text = process_text(text)

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


if __name__ == "__main__":
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
