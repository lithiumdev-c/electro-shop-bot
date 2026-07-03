from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import category_items, get_categories
from config import URL_SPONSOR_1, URL_SPONSOR_2

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина")],
        [KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Ваш профиль")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт ниже",
)

ad = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подпишитесь на спонсора 1", url=URL_SPONSOR_1)],
        [InlineKeyboardButton(text="Подпишитесь на спонсора 2", url=URL_SPONSOR_2)],
        [InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")],
    ]
)


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name, callback_data=f"category_{category.id}"
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
