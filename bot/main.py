from dotenv import load_dotenv
load_dotenv()
import asyncio
from datetime import datetime
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

import sqlite3

user_state = {}

prices = {
    "Разовый": "300₽",
    "Недельный": "500₽",
    "Месячный": "1000₽",
    "Годовой": "20000₽"
}


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
            [KeyboardButton(text="Разовый"), KeyboardButton(text="Недельный")],
            [KeyboardButton(text="Месячный"), KeyboardButton(text="Годовой")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


def confirm_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Оплатить")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )


def subscription_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Удалить абонемент")],
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


def format_date(date_str):
    return datetime.fromisoformat(date_str).strftime("%d.%m.%Y %H:%M")


def delete_subscription(telegram_id):
    conn = sqlite3.connect("data/database.db")
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM subscriptions
    WHERE user_id = (
        SELECT id FROM users WHERE telegram_id=?
    )
    """, (telegram_id,))

    conn.commit()
    conn.close()


# -------- УВЕДОМЛЕНИЯ --------
async def check_notifications(bot: Bot):
    while True:
        conn = sqlite3.connect("data/database.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT u.telegram_id, s.expires_at, s.visits_left, s.status
        FROM subscriptions s
        JOIN users u ON s.user_id = u.id
        """)

        rows = cur.fetchall()
        conn.close()

        for telegram_id, expires_at, visits, status in rows:
            expires = datetime.fromisoformat(expires_at)
            days_left = (expires - datetime.now()).days

            if status == "active":
                if days_left == 1:
                    await bot.send_message(telegram_id, "Абонемент скоро закончится (1 день)")
                if days_left <= 0:
                    await bot.send_message(telegram_id, "Абонемент закончился")
                if visits == 0:
                    await bot.send_message(telegram_id, "Закончились посещения")

        await asyncio.sleep(60)


async def main():
    print("Бот запускается...")

    init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    asyncio.create_task(check_notifications(bot))

    @dp.message(Command("start"))
    async def start_handler(message: Message):
        await message.answer("Добро пожаловать!", reply_markup=main_menu())

    @dp.message(lambda m: m.text == "Купить абонемент")
    async def buy(message: Message):
        await message.answer("Выбери тариф:", reply_markup=tariff_menu())

    @dp.message(lambda m: m.text in prices.keys())
    async def choose_tariff(message: Message):
        user_state[message.from_user.id] = message.text

        await message.answer(
            f"Тариф: {message.text}\nСтоимость: {prices[message.text]}",
            reply_markup=confirm_menu()
        )

    @dp.message(lambda m: m.text == "Оплатить")
    async def pay(message: Message):
        tariff = user_state.get(message.from_user.id)

        if not tariff:
            await message.answer("Ошибка", reply_markup=main_menu())
            return

        user_id = create_user(message.from_user.id)
        create_subscription(user_id, tariff)

        await message.answer("Оплата успешна!", reply_markup=main_menu())

    @dp.message(lambda m: m.text == "Мой абонемент")
    async def my_sub(message: Message):
        update_subscription_status(message.from_user.id)
        sub = get_subscription(message.from_user.id)

        if not sub:
            await message.answer("Нет абонемента")
            return

        _, type_, visits, expires, status, client_id, _ = sub

        await message.answer(
            f"ID: {client_id}\n"
            f"Тип: {type_}\n"
            f"Осталось посещений: {visits}\n"
            f"До: {format_date(expires)}\n"
            f"Статус: {status}",
            reply_markup=subscription_menu()
        )

    @dp.message(lambda m: m.text == "Удалить абонемент")
    async def delete_sub(message: Message):
        delete_subscription(message.from_user.id)
        await message.answer("Абонемент удалён", reply_markup=main_menu())

    @dp.message(lambda m: m.text == "Показать QR")
    async def qr(message: Message):
        update_subscription_status(message.from_user.id)
        sub = get_subscription(message.from_user.id)

        if not sub:
            await message.answer("Нет доступа")
            return

        client_id = sub[5]

        await message.answer(f"Ваш ID: {client_id}", reply_markup=qr_menu())

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