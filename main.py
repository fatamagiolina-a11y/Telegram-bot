import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8659770527:AAHH5j7I5-QqwO8CvHZ6CgqqnMr5Kda-Prw"
CHANNEL_ID = "@brandpills"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(content_types=["photo", "video", "text"])
async def handle_post(message: types.Message):

    text = message.caption if message.caption else message.text
    if not text:
        return

    items = text.split("\n\n")
    final_text = ""

    for item in items:
        item_text = ""
        lines = item.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 🔹 РАЗМЕРЫ (умные)
            if re.search(r'(размер\s*\d+)', line.lower()) or \
               re.fullmatch(r'\d{2}', line) or \
               re.search(r'\b(S|M|L|XL)\b', line):
                item_text += "📏 Размеры: " + line + "\n"
                continue

            # 🔹 ЦЕНА (умная)
            if re.search(r'\d+', line):
                clean_price = re.sub(r'[^\d]', '', line)
                if clean_price:
                    line = f"💸 {clean_price}€  (-40%)"

            item_text += line + "\n"

        final_text += item_text + "\n"

    # 🔹 ссылка
    final_text += "📲 Заказать: https://wa.me/393516282355"

    # 🔹 отправка
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
