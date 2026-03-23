import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")

# ВСТАВИМ ТВОЙ ID ПОСЛЕ
TARGET_CHAT_ID = 2028499794


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Это бот PIKANTO 🔥")


# 👉 получить свой ID
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш ID: {update.message.chat_id}")


# 👉 пересылка из канала + WhatsApp
async def forward_from_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        caption = update.channel_post.caption or update.channel_post.text or ""

        new_caption = f"{caption}\n\n📲 Заказать в WhatsApp: https://wa.me/393516282355"

        if update.channel_post.photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=update.channel_post.photo[-1].file_id,
                caption=new_caption
            )
        else:
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=new_caption
            )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", get_id))
app.add_handler(MessageHandler(filters.ALL, forward_from_channel))

app.run_polling()
