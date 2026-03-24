from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChannelPostHandler

# 🔐 ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = "8659770527:AAEvO0PsPMPOwDvZA0G6d5TX2XdqmdK8cDU"

# 📩 ТВОЙ TELEGRAM ID
TARGET_CHAT_ID = 2028499794

# 💬 команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PIKANTO bot работает 🔥")

# 📢 обработка постов из канала
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.channel_post

        if not message:
            return

        # безопасно получаем текст
        text = ""
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text

        # добавляем WhatsApp ссылку
        text = f"{text}\n\n📲 Заказать: https://wa.me/393516282355"

        # если есть фото
        if message.photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=message.photo[-1].file_id,
                caption=text
            )
        else:
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=text
            )

    except Exception as e:
        print("ERROR:", e)

# 🚀 запуск
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChannelPostHandler(handle_channel_post))

app.run_polling()
