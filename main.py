from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ChannelPostHandler

TOKEN = "8659770527:AAEvO0PsPMPOwDvZA0G6d5TX2XdqmdK8cDU"
TARGET_CHAT_ID = 2028499794

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PIKANTO bot работает 🔥")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post

    text = ""
    if message.caption:
        text = message.caption
    elif message.text:
        text = message.text

    text += "\n\n📲 Заказать: https://wa.me/393516282355"

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

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChannelPostHandler(handle_channel_post))

app.run_polling()
