import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup

API_TOKEN = "8659770527:AAFU1T-Po7nziaK16hiNPIHFIKgwdl9lC4w"
CHANNEL_ID = "@brandpils"

ALLOWED_USERS = [1666542263, 1637194418, 2028499794]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

media_groups = {}
pending_posts = {}

queue = []
queue_enabled = False
posting_enabled = False
interval_minutes = 5


# --- меню ---
def get_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("▶️ Старт", "⏹ Стоп")
    kb.add("🧾 Очередь ВКЛ", "❌ Очередь ВЫКЛ")
    kb.add("⚡ Сейчас", "⏭ Пропуск")
    kb.add("📊 Статус")
    return kb


# --- бренды ---
KNOWN_BRANDS = [
    "max mara", "ermanno scervino", "scervino",
    "pinko", "gucci", "prada", "n21", "zara", "dior"
]


def detect_brand(text):
    text_lower = text.lower()

    for brand in KNOWN_BRANDS:
        if brand in text_lower:
            return brand.upper()

    for line in text.split("\n"):
        if line.isupper() and len(line.split()) <= 3:
            return line

    return None


# --- категории ---
def detect_category(text):
    text = text.lower()

    if any(w in text for w in ["сапог","бот","туф","кроссов","мюл","босонож","сандал"]):
        return "shoes"

    if any(w in text for w in ["сумк","клатч"]):
        return "bag"

    if any(w in text for w in ["плать","куртк","юбк","пиджак","жакет","поло","рубаш"]):
        return "clothes"

    if any(w in text for w in ["ремень","платок","шарф","украш"]):
        return "accessories"

    return None


# --- проверки ---
def is_size_line(line):
    return bool(re.search(r'(\b\d{2}[\.\s\-]?){2,}', line)) or "размер" in line.lower()


def is_price_line(line):
    return "€" in line or "eur" in line.lower() or "цена" in line.lower()


# --- МУЛЬТИБРЕНД ОБРАБОТКА ---
def process_text(text):

    blocks = []
    current = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        # новый товар = КАПС бренд
        if line.isupper() and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)

    if current:
        blocks.append(current)

    final = ""
    hashtags = set()

    for block in blocks:

        block_text = "\n".join(block)

        brand = detect_brand(block_text)
        category = detect_category(block_text)

        if brand:
            final += f"{brand}\n"

        for line in block:

            if brand and line == brand:
                continue

            if is_size_line(line):
                final += "📏 Размеры: " + line + "\n"
                continue

            if is_price_line(line):
                price = re.sub(r'[^\d]', '', line)
                if price:
                    final += f"💰 {price}€ (-40%)\n"
                    continue

            final += line + "\n"

        final += "\n"

        if brand:
            hashtags.add(f"#{brand.lower().replace(' ', '')}")

        if category:
            hashtags.add(f"#{category}")

    if hashtags:
        final += " ".join(hashtags)

    return final


# --- отправка ---
async def send_post(data):
    try:
        if data["type"] == "photo":
            await bot.send_photo(
                CHANNEL_ID,
                data["file"],
                caption=data["text"] + "\n🛒 Заказать: https://wa.me/393516282355"
            )

        elif data["type"] == "video":
            await bot.send_video(
                CHANNEL_ID,
                data["file"],
                caption=data["text"]
            )

        elif data["type"] == "text":
            await bot.send_message(
                CHANNEL_ID,
                data["text"] + "\n🛒 Заказать: https://wa.me/393516282355"
            )

        elif data["type"] == "album":
            await bot.send_media_group(CHANNEL_ID, data["media"])

    except Exception as e:
        print("SEND ERROR:", e)


# --- очередь ---
async def queue_worker():
    while True:
        if posting_enabled and queue:
            post = queue.pop(0)
            await send_post(post)
        await asyncio.sleep(interval_minutes * 60)


# --- управление ---
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот готов 🚀", reply_markup=get_menu())


@dp.message_handler(lambda m: m.text == "🧾 Очередь ВКЛ")
async def q_on(message: types.Message):
    global queue_enabled
    queue_enabled = True
    await message.answer("Очередь включена")


@dp.message_handler(lambda m: m.text == "❌ Очередь ВЫКЛ")
async def q_off(message: types.Message):
    global queue_enabled
    queue_enabled = False
    await message.answer("Очередь выключена")


@dp.message_handler(lambda m: m.text == "▶️ Старт")
async def start_post(message: types.Message):
    global posting_enabled
    posting_enabled = True
    await message.answer("Автопостинг запущен")


@dp.message_handler(lambda m: m.text == "⏹ Стоп")
async def stop_post(message: types.Message):
    global posting_enabled
    posting_enabled = False
    await message.answer("Автопостинг остановлен")


@dp.message_handler(lambda m: m.text == "📊 Статус")
async def status(message: types.Message):
    await message.answer(f"В очереди: {len(queue)}")


@dp.message_handler(lambda m: m.text == "⚡ Сейчас")
async def now(message: types.Message):
    if queue:
        post = queue.pop(0)
        await send_post(post)


@dp.message_handler(lambda m: m.text == "⏭ Пропуск")
async def skip(message: types.Message):
    if queue:
        queue.pop(0)


# --- обработка ---
@dp.message_handler(content_types=["photo","video","text"])
async def handle_post(message: types.Message):

    if message.from_user.id not in ALLOWED_USERS:
        return

    user_id = message.from_user.id

    # альбом
    if message.media_group_id:
        group_id = message.media_group_id
        media_groups.setdefault(group_id, []).append(message)

        await asyncio.sleep(2)
        msgs = media_groups.get(group_id)

        if not msgs or message != msgs[-1]:
            return

        text = next((m.caption for m in msgs if m.caption), "")
        final = process_text(text)

        media = []
        for i, m in enumerate(msgs):
            media.append(types.InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=final if i == 0 else None
            ))

        post_data = {"type":"album","media":media}

        if queue_enabled:
            queue.append(post_data)
        else:
            await send_post(post_data)

        media_groups.pop(group_id, None)
        return

    # фото/видео
    if message.photo or message.video:
        text = message.caption or ""

        if text:
            final = process_text(text)
            post_data = {
                "type":"photo" if message.photo else "video",
                "file": message.photo[-1].file_id if message.photo else message.video.file_id,
                "text": final
            }

            if queue_enabled:
                queue.append(post_data)
            else:
                await send_post(post_data)
            return

        pending_posts[user_id] = message
        await asyncio.sleep(3)

        if user_id in pending_posts:
            msg = pending_posts[user_id]
            final = process_text("")

            post_data = {
                "type":"photo" if msg.photo else "video",
                "file": msg.photo[-1].file_id if msg.photo else msg.video.file_id,
                "text": final
            }

            if queue_enabled:
                queue.append(post_data)
            else:
                await send_post(post_data)

            pending_posts.pop(user_id, None)
        return

    # текст
    if message.text:
        if user_id in pending_posts:
            msg = pending_posts[user_id]
            final = process_text(message.text)

            post_data = {
                "type":"photo" if msg.photo else "video",
                "file": msg.photo[-1].file_id if msg.photo else msg.video.file_id,
                "text": final
            }

            if queue_enabled:
                queue.append(post_data)
            else:
                await send_post(post_data)

            pending_posts.pop(user_id, None)
            return

        final = process_text(message.text)
        post_data = {"type":"text","text":final}

        if queue_enabled:
            queue.append(post_data)
        else:
            await send_post(post_data)


# --- запуск ---
if __name__ == "__main__":
    async def main():
        asyncio.create_task(queue_worker())
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
