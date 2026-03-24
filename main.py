from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ChannelPostHandler,
)

# 🔐 ТВОЙ TOKEN
TOKEN = "8659770527:AAH4cb-P-Trqxc6IjTDVJHGEX-ZP2K6Lfio"

# ❤️ ТВОЙ TELEGRAM ID (куда пересылать)
TARGET_CHAT_ID = 2028499774


# 💬 команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PIKANTO bot работает 🔥")


# 📢 обработка постов из канала
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("CHAT TYPE:", update.effective_chat.type)
        print("CHAT ID:", update.effective_chat.id)

        message = update.effective_message

        if not message:
            return

        # берём текст или caption
        text = ""
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text

        # добавляем ссылку
        text = f"{text}\n\n📲 Заказать: https://wa.me/393516282355"

        # если фото
        if message.photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=text,
            )
        else:
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=text,
            )

    except Exception as e:
        print("ERROR:", e)


# 🚀 запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# ❗️КЛЮЧЕВОЕ — обработчик канала
app.add_handler(ChannelPostHandler(handle_channel_post))

# 🔥 убираем webhook конфликт
app.bot.delete_webhook(drop_pending_updates=True)

app.run_polling()
