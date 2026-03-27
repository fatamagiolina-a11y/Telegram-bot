import os
import re
import time
from collections import deque

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")

# 👉 ВСТАВЬ СЮДА ID КАНАЛА
CHANNEL_ID = "@brandpils"


# ====== СПИСОК БРЕНДОВ ======
BRANDS = [
    "VIVETTA","MSGM","N21","GCDS","ICEBERG","ICE PLAY","DSQUARED2",
    "PHILIPP PLEIN","PLEIN SPORT","JOHN RICHMOND","RICHMOND X",
    "LOVE MOSCHINO","MOSCHINO","KARL LAGERFELD","MAX MARA",
    "MAX MARA STUDIO","MAX MARA LEISURE","WEEKEND MAX MARA",
    "MARELLA","EMME MARELLA","IBLUES","LIU JO","LIU JO SPORT",
    "LIU JO BEACHWEAR","LIU JO JEANS","PINKO","PATRIZIA PEPE",
    "TWINSET","ELISABETTA FRANCHI","GAELLE","IMPERIAL","ANIYE BY",
    "ESSENTIEL ANTWERP","ESSENTIEL","PLEASE","SILVIAN HEACH",
    "ODI ET AMO","RELISH","VICOLO","RINASCIMENTO","DENNY ROSE",
    "FRACOMINA","GUESS","GUESS BY MARCIANO","ARMANI EXCHANGE",
    "EA7","EMPORIO ARMANI","VERSACE JEANS COUTURE","CAVALLI CLASS",
    "ROBERTO CAVALLI","JUST CAVALLI","TRUSSARDI","FURLA","COCCINELLE",
    "POLLINI","ALVIERO MARTINI","1A CLASSE","THEMOIRÈ","LA MILANESA",
    "VEE COLLECTIVE","GIANNI CHIARINI","CULTI MILANO","FABIANA FILIPPI",
    "FALERIO SARTI","ERMANNO SCERVINO","ERMANNO FIRENZE",
    "ERMANNO SCERVINO LIFE","BLANCHA","DE SIENA","AIM",
    "AVENUE 67 MILANO","COUNTY OF MILAN","D'EXTERIOR",
    "GIUSEPPE DI MORABITO","JACOB COHEN","SHAFT JEANS",
    "ICEBERG JEANS","PAPERLACE","POEVE","SEVENTY","THE ANTIPODE",
    "NATASHA ZINKO","PERSONA BY MARINA RINALDI","MM"
]


# ====== КАТЕГОРИИ ======
CATEGORIES = {
    "ПАЛЬТО": ["пальто","coat"],
    "КУРТКА": ["куртка","jacket"],
    "ПЛАТЬЕ": ["платье","dress"],
    "ЮБКА": ["юбка","skirt"],
    "БРЮКИ": ["брюки","pants"],
    "ДЖИНСЫ": ["джинсы","jeans"],
    "КОФТА": ["кофта","sweater","maglia"],
    "СУМКА": ["сумка","bag"],
    "ОБУВЬ": ["обувь","scarpe","shoes"],
    "АКСЕССУАР": ["accessori","аксессуар"]
}


# ====== ОЧЕРЕДЬ ======
queue = deque()


# ====== ПОИСК БРЕНДА ======
def detect_brand(text):
    text_upper = text.upper()
    for brand in BRANDS:
        if brand in text_upper:
            return brand
    return "PIKANTO"


# ====== ПОИСК КАТЕГОРИИ ======
def detect_category(text):
    text_lower = text.lower()
    for cat, words in CATEGORIES.items():
        for w in words:
            if w in text_lower:
                return cat
    return "STYLE"


# ====== ПОИСК ЦЕНЫ ======
def detect_price(text):
    price = re.search(r"\d+\s?€|\€\s?\d+", text)
    discount = re.search(r"-\s?\d+%", text)

    price_str = price.group(0).replace(" ", "") if price else ""
    discount_str = discount.group(0).replace(" ", "") if discount else ""

    return f"{price_str} {discount_str}".strip()


# ====== ФОРМИРОВАНИЕ ТЕКСТА ======
def format_caption(text):
    brand = detect_brand(text)
    category = detect_category(text)
    price = detect_price(text)

    caption = f"{brand}\n{category}\n{price}\n\n#{category} #{brand}\n\n📲 Заказать: https://wa.me/393516282355"
    return caption


# ====== /start ======
def start(update: Update, context: CallbackContext):
    update.message.reply_text("PIKANTO bot работает 🔥")


# ====== ПРИЁМ СООБЩЕНИЙ ======
def handle_message(update: Update, context: CallbackContext):
    message = update.message

    if not message:
        return

    text = message.caption if message.caption else message.text if message.text else ""

    caption = format_caption(text)

    item = {
        "photo": message.photo[-1].file_id if message.photo else None,
        "text": caption
    }

    queue.append(item)


# ====== ОТПРАВКА КАЖДЫЕ 5 МИН ======
def process_queue(context: CallbackContext):
    if not queue:
        return

    item = queue.popleft()

    if item["photo"]:
        context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=item["photo"],
            caption=item["text"]
        )
    else:
        context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=item["text"]
        )


# ====== ЗАПУСК ======
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.all, handle_message))

    updater.job_queue.run_repeating(process_queue, interval=300, first=10)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
