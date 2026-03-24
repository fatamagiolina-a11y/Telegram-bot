from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# 🔐 ТВОЙ ТОКЕН
TOKEN = "8659770527:AAEvO0PsPMPOwDvZA0G6d5TX2XdqmdK8cDU"

# 📩 ТВОЙ ID
TARGET_CHAT_ID = 2028499794

# 💬 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PIKANTO bot работает 🔥")

# 📢 обработка постов канала
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.channel_post

        # ❗ если это не пост канала — игнор
        if not message:
            return

        text = ""

        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text

        text = f"{text}\n\n📲 Заказать: https://wa.me/393516282355"

        # 📸 если фото
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

# 🔥 ВАЖНО — ловим ВСЁ и фильтруем внутри
app.add_handler(MessageHandler(filters.ALL, handle_channel_post))

app.run_polling()
