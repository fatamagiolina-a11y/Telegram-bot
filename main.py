import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8659770527:AAFU1T-Po7nziaK16hiNPIHFIKgwdl9lC4w"
CHANNEL_ID = "@brandpils"
USER_ID = 1666542263  # ← вставь свой ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Бот работает ✅ Отправь фото или видео")

@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    # 🔒 принимаем только от тебя
   # if message.from_user.id != USER_ID:
   #     return

    text = message.caption or message.text or ""

    items = text.split("\n\n")
    final_text = ""

    for item in items:
        item_text = ""
        lines = item.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 📏 Размеры
            if re.search(r'(размер)', line.lower()) or \
               re.search(r'\d{2}\.\d{2}', line) or \
               re.search(r'\b(S|M|L|XL)\b', line):
                item_text += "📏 Размеры: " + line + "\n"
                continue

            # 💸 Цена
            if re.search(r'\d+', line):
                clean_price = re.sub(r'[^\d]', '', line)
                if clean_price:
                    line = f"💸 {clean_price}€  (-40%)"

            item_text += line + "\n"

        final_text += item_text + "\n"

    final_text += "📲 Заказать: https://wa.me/393516282355"

    # 🚀 отправка
    try:
        if message.video:
            await bot.send_video(
                CHANNEL_ID,
                message.video.file_id,
                caption=final_text
            )

        elif message.photo:
            await bot.send_photo(
                CHANNEL_ID,
                message.photo[-1].file_id,
                caption=final_text
            )

        else:
            await bot.send_message(
                CHANNEL_ID,
                final_text
            )

    except Exception as e:
        print("ERROR:", e)





if __name__ == "__main__":
    import asyncio

    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling()

    asyncio.run(main())
