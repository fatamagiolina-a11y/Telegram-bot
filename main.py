import os
os.system("pip install python-telegram-bot==13.15")

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔐 ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = "8659770527:AAH4cb-P-Trqxc6IjTDVJHGEX-ZP2K6Lfio"

# ❤️ ТВОЙ TELEGRAM ID
TARGET_CHAT_ID = 2028499774


def start(update: Update, context: CallbackContext):
    update.message.reply_text("PIKANTO bot работает 🔥")


def handle_channel_post(update: Update, context: CallbackContext):
    try:
        message = update.channel_post

        if not message:
            return

        text = ""
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text

        # 🔥 добавляем WhatsApp ссылку
        text = text + "\n\n📲 Заказать: https://wa.me/393516282355"

        if message.photo:
            context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=text
            )
        else:
            context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=text
            )

    except Exception as e:
        print("ERROR:", e)


updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.chat_type.channel, handle_channel_post))

updater.start_polling()
updater.idle()
