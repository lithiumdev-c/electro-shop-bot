import os

from aiocryptopay import AioCryptoPay, Networks
from aiogram.methods import create_invoice_link
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from app.database.requests import category_items, get_categories

load_dotenv()

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="О нас")],
        [KeyboardButton(text="Ваш профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт ниже",
)

ad = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подпишитесь на спонсора 1", url=str(os.getenv("URL_SPONSOR_1"))
            )
        ],
        [
            InlineKeyboardButton(
                text="Подпишитесь на спонсора 2", url=str(os.getenv("URL_SPONSOR_2"))
            )
        ],
        [InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")],
    ]
)


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{category.name}", callback_data=f"category_{category.id}"
            )
        )
    keyboard.add(InlineKeyboardButton(text="На главную", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()


async def items(category_id):
    all_items = await category_items(category_id)
    keyboard = InlineKeyboardBuilder()

    for item in all_items:
        keyboard.add(
            InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}")
        )
    keyboard.add(InlineKeyboardButton(text="На главную", callback_data="to_main"))
    return keyboard.adjust(2).as_markup()


async def payment(item_id: int, price_usd: float, user_id: int, category_id: int):
    keyboard = InlineKeyboardBuilder()
    crypto = AioCryptoPay(
        token=str(os.getenv("CRYPTO_TOKEN")), network=Networks.TEST_NET
    )

    invoice = await crypto.create_invoice(
        amount=float(price_usd),
        fiat="USD",
        currency_type="fiat",
        payload=f"{user_id}_{item_id}",
    )

    keyboard.add(
        InlineKeyboardButton(
            text=f"💳 Оплатить ${price_usd}",
            url=invoice.bot_invoice_url,
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text="Проверить оплату",
            callback_data=f"check_payment_{invoice.invoice_id}",
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text="Назад к товарам",
            callback_data=f"category_{category_id}",
        )
    )
    await crypto.close()
    return keyboard.adjust(1, 2).as_markup()
