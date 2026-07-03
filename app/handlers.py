import logging
import os

from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot, F, Router
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.utils.text_decorations import MarkdownDecoration
from dotenv import load_dotenv

import app.database.requests as rq
import app.keyboards as kb

router = Router()
load_dotenv()


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()


channels = os.getenv("CHANNELS_CHECK", "").split(",")
CRYPTO_TOKEN: str = str(os.getenv("CRYPTO_TOKEN"))

if CRYPTO_TOKEN is None:
    raise ValueError("CRYPTO_TOKEN is not set")


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    for chat_id in channels:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            logging.error(f"Ошибка подписки: {e}")
    return True


@router.message(CommandStart(), F.from_user)
async def start(msg: Message):
    if not msg.from_user:
        return
    await rq.set_user(msg.from_user.id)
    name = msg.from_user.first_name
    await msg.answer(
        f"👾{name} Добро-пожаловать в Electro-Shop!\nПеред тем как перейти к покупкам подпишитесь на наших спонсоров!",
        reply_markup=kb.ad,
    )


@router.callback_query(F.data == "check_subscription" or F.data == "to_main")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="Успех! Вы подписались на спонсоров.\n👾Добро пожаловать в Electro-Shop!\nИспользуйте клавиатуру предоставленную ниже!",
            reply_markup=kb.main,
        )
    else:
        await callback.answer(
            "Вы не подписаны на спонсоров! Проверьте еще раз!", show_alert=True
        )


@router.message(F.text == "Каталог")
async def catalog(msg: Message, bot: Bot):
    if msg.from_user is None:
        return
    if await is_subscribed(bot, msg.from_user.id):
        await msg.answer(
            "Выберите категорию товара:", reply_markup=await kb.categories()
        )
    else:
        await msg.answer("⛔ Вы не подписаны на наших спонсоров!", reply_markup=kb.ad)


@router.callback_query(F.data.startswith("category_"))
async def category(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        if callback.message is None or callback.data is None:
            return
        await callback.answer("Вы выбрали категорию", show_alert=True)
        await callback.message.answer(
            "Выберите товар по категории:",
            reply_markup=await kb.items(int(callback.data.split("_")[1])),
        )
    else:
        if callback.message is None:
            return
        await callback.message.answer("Вы не подписались на спонсоров!")


@router.callback_query(F.data.startswith("item_"))
async def item(callback: CallbackQuery, bot: Bot):
    if callback.message is None or callback.data is None:
        return
    if await is_subscribed(bot, callback.from_user.id):
        item_data = await rq.get_item(item_id=int(callback.data.split("_")[1]))
        if item_data is None:
            return
        await callback.answer("Вы выбрали товар", show_alert=True)
        crypto = AioCryptoPay(token=CRYPTO_TOKEN, network=Networks.TEST_NET)

        caption_txt = (
            f"**{item_data.name}**\n"
            f"Описание: {item_data.description}\n"
            f"Цена: {item_data.price}$"
        )

        payment_markup = await kb.payment(
            item_id=item_data.id,
            price_usd=float(item_data.price),
            user_id=callback.from_user.id,
            category_id=item_data.category,
        )

        await callback.message.answer_photo(
            photo=item_data.image,
            caption=caption_txt,
            reply_markup=payment_markup,
            parse_mode="Markdown",
        )
        await crypto.close()
    else:
        if callback.message is None:
            return
        await callback.message.answer("Вы не подписались на спонсоров!")
