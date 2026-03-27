import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8659770527:AAHH5j7I5-QqwO8CvHZ6CgqqnMr5Kda-Prw"
CHANNEL_ID = "@brandpils"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# =========================
# 📦 ХРАНЕНИЕ МЕДИА
# =========================

user_data = {}

# =========================
# 🏷 БРЕНДЫ (очищенные)
# =========================

BRANDS = [
    "AIM", "AVENUE 67 MILANO", "BLANCHA", "COUNTY OF MILAN",
    "CULTI MILANO", "D'EXTERIOR", "DE SIENA", "DSQUARED2",
    "ERMANNO FIRENZE", "ERMANNO SCERVINO LIFE", "ESSENTIVE",
    "FABIANA FILIPPI", "FALIERO SARTI", "GCDS",
    "GIUSEPPE DI MORABITO", "ICE PLAY", "ICEBERG",
    "ICEBERG JEANS", "JACOB COHEN", "JOHN RICHMOND",
    "KARL LAGERFELD", "LA MILANESA", "LIU JO",
    "LOVE MOSCHINO", "MARELLA", "MAX MARA",
    "MSGM", "N21", "NATASHA ZINKO",
    "PAPERLACE", "PERSONA BY MARINA RINALDI",
    "POEVE", "SEVENTY", "SHAFT JEANS",
    "THE ANTIPODE", "THEMOIRÈ", "VEE COLLECTIVE",
    "VERSACE JEANS COUTURE", "VIVETTA",
    "WEEKEND"
]

# --- бренд
def detect_brand(text):
    t = text.upper()

    if "WEEKEND" in t:
        return "WEEKEND"
    if "MAX MARA" in t:
        return "MAX MARA"
    if "MARELLA" in t:
        return "MARELLA"

    for b in BRANDS:
        if b in t:
            return b

    return ""

# =========================
# 👗 КАТЕГОРИЯ
# =========================

def detect_category(text):
    t = text.lower()

    if "платье" in t:
        return "платье"
    if "куртка" in t:
        return "куртка"
    if "костюм" in t:
        return "костюм"
    if "пальто" in t:
        return "пальто"
    if "джинсы" in t:
        return "джинсы"

    return "товар"

# =========================
# 📏 РАЗМЕРЫ (твоя версия FIX)
# =========================

VALID_SIZES = {
    "36","37","38","39","40","42","44","46",
    "XS","S","M","L","XL"
}

def extract_sizes(text):
    words = re.findall(r'\b[A-Z0-9]+\b', text.upper())

    sizes = []
    for w in words:
        if w in VALID_SIZES:
            sizes.append(w)

    sizes = list(dict.fromkeys(sizes))

    return " ".join(sizes)

# =========================
# ✍️ ТЕКСТ
# =========================

def build_caption(text):
    brand = detect_brand(text)
    category = detect_category(text)
    sizes = extract_sizes(text)

    hashtags = ""
    if brand:
        hashtags += f"#{brand.lower().replace(' ', '')} "
    hashtags += f"#{category}"

    return f"""
{text}

📏 Размеры: {sizes}

💸 -40%

{hashtags}

📲 Заказать:
https://wa.me/393516282355
"""

# =========================
# 📸 СОХРАНЕНИЕ МЕДИА (FIX АЛЬБОМА)
# =========================

@dp.message_handler(content_types=['photo', 'video'])
async def save_media(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {
            "media": [],
            "media_group_id": None
        }

    # альбом
    if message.media_group_id:
        if user_data[user_id]["media_group_id"] != message.media_group_id:
            user_data[user_id]["media"] = []
            user_data[user_id]["media_group_id"] = message.media_group_id

    user_data[user_id]["media"].append(message)

# =========================
# 📝 ТЕКСТ → ПУБЛИКАЦИЯ
# =========================

@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data or not user_data[user_id]["media"]:
        return

    media_messages = user_data[user_id]["media"]
    caption = build_caption(message.text)

    # --- одно медиа
    if len(media_messages) == 1:
        msg = media_messages[0]

        if msg.photo:
            await bot.send_photo(
                CHANNEL_ID,
                photo=msg.photo[-1].file_id,
                caption=caption
            )

        elif msg.video:
            await bot.send_video(
                CHANNEL_ID,
                video=msg.video.file_id,
                caption=caption
            )

    # --- альбом
    else:
        media_group = []

        for i, msg in enumerate(media_messages):
            if msg.photo:
                item = types.InputMediaPhoto(
                    media=msg.photo[-1].file_id
                )
            elif msg.video:
                item = types.InputMediaVideo(
                    media=msg.video.file_id
                )
            else:
                continue

            if i == 0:
                item.caption = caption

            media_group.append(item)

        await bot.send_media_group(CHANNEL_ID, media_group)

    # очистка
    user_data[user_id] = {"media": [], "media_group_id": None}

# =========================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
