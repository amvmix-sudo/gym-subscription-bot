import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from bot.config import BOT_TOKEN


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить абонемент")],
            [KeyboardButton(text="Мой абонемент")],
            [KeyboardButton(text="Показать QR")],
        ],
        resize_keyboard=True
    )


async def main():
    print("Бот запускается...")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # --- /start ---
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        await message.answer(
            "Добро пожаловать в систему абонементов!",
            reply_markup=main_menu()
        )

    # --- Кнопка: Купить абонемент ---
    @dp.message(lambda message: message.text == "Купить абонемент")
    async def buy_subscription(message: Message):
        await message.answer(
            "Выберите тип абонемента:\n\n"
            "Разовый — 300₽ (1 посещение, 3 дня)\n"
            "Недельный — 500₽ (2 посещения, 7 дней)\n"
            "Месячный — 1000₽ (8 посещений, 31 день)\n"
            "Годовой — 20000₽ (96 посещений, 365 дней)"
        )

    # --- Кнопка: Мой абонемент ---
    @dp.message(lambda message: message.text == "Мой абонемент")
    async def my_subscription(message: Message):
        await message.answer("У вас пока нет активного абонемента.")

    # --- Кнопка: Показать QR ---
    @dp.message(lambda message: message.text == "Показать QR")
    async def show_qr(message: Message):
        await message.answer("У вас нет абонемента.")

    print("Polling стартует...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("Ошибка:", e)