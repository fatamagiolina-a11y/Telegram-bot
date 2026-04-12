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

# 🔥 НОВОЕ
queue = []
queue_enabled = False
posting_enabled = False
interval_minutes = 5


# =========================
# 🧠 ОБРАБОТКА ТЕКСТА (НЕ ТРОГАЛ)
# =========================
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


# =========================
# 🎛 КНОПКИ
# =========================
def get_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("▶️ Старт", "⏹ Стоп")
    kb.add("🧾 Очередь ВКЛ", "❌ Очередь ВЫКЛ")
    kb.add("⚡ Сейчас", "⏭ Пропуск")
    kb.add("📊 Статус")
    return kb


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот готов 🚀", reply_markup=get_menu())


# =========================
# 🔥 ОТПРАВКА (ВЫНЕСЕНА)
# =========================
async def send_post(data):

    try:
        if data["type"] == "video":
            await bot.send_video(CHANNEL_ID, data["file"], caption=data["text"])

        elif data["type"] == "photo":
            await bot.send_photo(CHANNEL_ID, data["file"], caption=data["text"])

        elif data["type"] == "text":
            await bot.send_message(CHANNEL_ID, data["text"])

        elif data["type"] == "album":
            await bot.send_media_group(CHANNEL_ID, data["media"])

    except Exception as e:
        print("SEND ERROR:", e)


# =========================
# ⏱ АВТОПОСТИНГ
# =========================
async def queue_worker():
    global queue

    while True:
        if posting_enabled and queue:
            post = queue.pop(0)
            await send_post(post)

        await asyncio.sleep(interval_minutes * 60)


# =========================
# 🎛 УПРАВЛЕНИЕ
# =========================
@dp.message_handler(lambda m: m.text == "🧾 Очередь ВКЛ")
async def queue_on(message: types.Message):
    global queue_enabled
    queue_enabled = True
    await message.answer("Очередь включена ✅")


@dp.message_handler(lambda m: m.text == "❌ Очередь ВЫКЛ")
async def queue_off(message: types.Message):
    global queue_enabled
    queue_enabled = False
    await message.answer("Очередь выключена ❌")


@dp.message_handler(lambda m: m.text == "▶️ Старт")
async def start_queue(message: types.Message):
    global posting_enabled
    posting_enabled = True
    await message.answer("Автопостинг запущен ▶️")


@dp.message_handler(lambda m: m.text == "⏹ Стоп")
async def stop_queue(message: types.Message):
    global posting_enabled
    posting_enabled = False
    await message.answer("Автопостинг остановлен ⏹")


@dp.message_handler(lambda m: m.text == "📊 Статус")
async def status(message: types.Message):
    await message.answer(f"В очереди: {len(queue)} постов")


@dp.message_handler(lambda m: m.text == "⚡ Сейчас")
async def now_post(message: types.Message):
    if queue:
        post = queue.pop(0)
        await send_post(post)
        await message.answer("Отправлено сейчас ⚡")


@dp.message_handler(lambda m: m.text == "⏭ Пропуск")
async def skip_post(message: types.Message):
    if queue:
        queue.pop(0)
        await message.answer("Пост пропущен ⏭")


# =========================
# 📦 ОСНОВНАЯ ЛОГИКА
# =========================
@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    # --- АЛЬБОМ ---
    if message.media_group_id:
        group_id = message.media_group_id

        if group_id not in media_groups:
            media_groups[group_id] = []

        media_groups[group_id].append(message)

        await asyncio.sleep(2)

        messages = media_groups.get(group_id)

        if not messages or len(messages) < 2:
            return

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

        post_data = {
            "type": "album",
            "media": media
        }

        if queue_enabled:
            queue.append(post_data)
        else:
            await send_post(post_data)

        media_groups.pop(group_id, None)
        return

    # --- ОДИНОЧНЫЙ ---
    text = message.caption or message.text or ""
    final_text = process_text(text)

    if message.video:
        post_data = {
            "type": "video",
            "file": message.video.file_id,
            "text": final_text
        }

    elif message.photo:
        post_data = {
            "type": "photo",
            "file": message.photo[-1].file_id,
            "text": final_text
        }

    else:
        post_data = {
            "type": "text",
            "text": final_text
        }

    if queue_enabled:
        queue.append(post_data)
    else:
        await send_post(post_data)


# =========================
# 🚀 ЗАПУСК
# =========================
if __name__ == "__main__":
    async def main():
        asyncio.create_task(queue_worker())
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
