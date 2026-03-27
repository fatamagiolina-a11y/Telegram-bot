import os
import re
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@brandpils"

# ===== БРЕНДЫ =====
BRANDS = [
    "VIVETTA","MSGM","N21","GCDS",
    "ICEBERG","ICE PLAY","DSQUARED2",
    "JOHN RICHMOND","LOVE MOSCHINO",
    "KARL LAGERFELD","MAX MARA","WEEKEND",
    "MARELLA","EMME MARELLA","IBLUES",
    "LIU JO","PINKO","TWINSET",
    "ELISABETTA FRANCHI","GAELLE",
    "ESSENTIEL","PLEASE","RELISH",
    "VICOLO","RINASCIMENTO"
]

# ===== КАТЕГОРИИ =====
CATEGORIES = [
    "ПАЛЬТО","КУРТКА","ПЛАТЬЕ","ЮБКА",
    "БРЮКИ","ДЖИНСЫ","КОСТЮМ",
    "СВИТЕР","ФУТБОЛКА",
    "ОБУВЬ","БАЛЕТКИ","ТУФЛИ","КРОССОВКИ",
    "СУМКА"
]

# ===== ПАМЯТЬ =====
user_data_store = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("PIKANTO bot работает 🔥")

# ===== СОХРАНЯЕМ МЕДИА =====
def handle_media(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in user_data_store:
        user_data_store[user_id] = {"photos": [], "video": None}

    # 🎥 видео
    if update.message.video:
        user_data_store[user_id]["video"] = update.message.video.file_id

    # 📸 фото (ВАЖНО: file_id)
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        user_data_store[user_id]["photos"].append(photo)

# ===== ОБРАБОТКА ТЕКСТА =====
def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.upper()

    data = user_data_store.get(user_id)

    if not data:
        return

    # бренд
    brand = next((b for b in BRANDS if b in text), "PIKANTO")

    # категория
    category = next((c for c in CATEGORIES if c in text), "STYLE")

    # ===== РАЗМЕРЫ =====
    sizes_match = re.findall(r"(XS|S|M|L|XL|\b\d{2,3}\b)", text)

    sizes_text = ""
    if sizes_match:
        sizes_text = "📏 Размеры: " + " ".join(sorted(set(sizes_match)))

    # ===== ЦЕНА =====
    price_match = re.search(r"\d+\s?€", text)

    if price_match:
        price = price_match.group().replace(" ", "")
        price_text = f"{price} -40%"
    else:
        price_text = ""

    # ===== ФИНАЛЬНЫЙ ТЕКСТ =====
    final_text = f"{brand}\n{category}\n"

    if sizes_text:
        final_text += f"{sizes_text}\n\n"

    if price_text:
        final_text += f"{price_text}\n"

    final_text += "\n📱 Заказать:\nhttps://wa.me/393516282355"

    # защита лимита
    final_text = final_text[:1000]

    try:
        # 🔥 ВИДЕО
        if data.get("video"):
            context.bot.send_video(
                chat_id=CHANNEL_ID,
                video=data["video"],
                caption=final_text
            )

        # 📸 ФОТО
        elif data.get("photos") and len(data["photos"]) > 0:
            media = []

            for i, photo in enumerate(data["photos"][:10]):
                if i == 0:
                    media.append(InputMediaPhoto(media=photo, caption=final_text))
                else:
                    media.append(InputMediaPhoto(media=photo))

            context.bot.send_media_group(chat_id=CHANNEL_ID, media=media)

        else:
            print("❌ НЕТ КОНТЕНТА")

    except Exception as e:
        print("ERROR:", e)

    # очистка
    user_data_store[user_id] = {"photos": [], "video": None}

# ===== ЗАПУСК =====
updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.photo | Filters.video, handle_media))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

updater.start_polling()
updater.idle()
