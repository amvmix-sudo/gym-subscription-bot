import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from bot.config import BOT_TOKEN
from bot.database import (
    init_db,
    create_user,
    create_subscription,
    get_subscription,
    update_subscription_status,
    decrement_visit
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить абонемент")],
            [KeyboardButton(text="Мой абонемент")],
            [KeyboardButton(text="Показать QR")],
        ],
        resize_keyboard=True
    )


def tariff_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Разовый")],
            [KeyboardButton(text="Недельный")],
            [KeyboardButton(text="Месячный")],
            [KeyboardButton(text="Годовой")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


def qr_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить посещение")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True
    )


async def main():
    print("Бот запускается...")

    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message):
        await message.answer("Добро пожаловать!", reply_markup=main_menu())

    @dp.message(lambda m: m.text == "Купить абонемент")
    async def buy(message: Message):
        await message.answer("Выбери тариф:", reply_markup=tariff_menu())

    @dp.message(lambda m: m.text in ["Разовый", "Недельный", "Месячный", "Годовой"])
    async def choose_tariff(message: Message):
        user_id = create_user(message.from_user.id)
        create_subscription(user_id, message.text)

        await message.answer(
            f"Абонемент '{message.text}' активирован!",
            reply_markup=main_menu()
        )

    @dp.message(lambda m: m.text == "Мой абонемент")
    async def my_sub(message: Message):
        update_subscription_status(message.from_user.id)
        sub = get_subscription(message.from_user.id)

        if not sub:
            await message.answer("Нет абонемента")
            return

        _, type_, visits, expires, status, client_id = sub

        await message.answer(
            f"ID: {client_id}\n"
            f"Тип: {type_}\n"
            f"Осталось посещений: {visits}\n"
            f"До: {expires}\n"
            f"Статус: {status}"
        )

    @dp.message(lambda m: m.text == "Показать QR")
    async def qr(message: Message):
        update_subscription_status(message.from_user.id)
        sub = get_subscription(message.from_user.id)

        if not sub:
            await message.answer("Нет доступа")
            return

        client_id = sub[5]

        await message.answer(
            f"Ваш QR (ID): {client_id}",
            reply_markup=qr_menu()
        )

    @dp.message(lambda m: m.text == "Подтвердить посещение")
    async def visit(message: Message):
        update_subscription_status(message.from_user.id)
        result = decrement_visit(message.from_user.id)
        await message.answer(result, reply_markup=main_menu())

    @dp.message(lambda m: m.text == "Назад")
    async def back(message: Message):
        await message.answer("Главное меню", reply_markup=main_menu())

    print("Polling стартует...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())