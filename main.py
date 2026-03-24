import os
from telegram import Update
from telegram.ext import ChannelPostHandler

TOKEN = 8659770527:AAEvO0PsPMPOwDvZA0G6d5TX2XdqmdK8cDU

TARGET_CHAT_ID = 2028499794

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это бот PIKANTO 🔥")

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post

    caption = message.caption if message.caption else message.text if message.text else ""
    new_caption = caption + "\n\n📲 Заказать: https://wa.me/393516282355

    if message.photo:
        await context.bot.send_photo(
            chat_id=TARGET_CHAT_ID,
            photo=message.photo[-1].file_id,
            caption=new_caption
        )
    else:
        await context.bot.send_message(
            chat_id=TARGET_CHAT_ID,
            text=new_caption
        )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChannelPostHandler(handle_channel_post))

app.run_polling()
