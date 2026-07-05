import time
from datetime import datetime

from aiogram import F, Router, html
from aiogram.types import Message

import database
import keyboards
from config import REFUND_WINDOW_SECONDS
from locales import get_all_translations, get_text

router = Router()


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


def format_date(timestamp):
    """Форматирует unix-время в читаемую дату."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d.%m.%Y %H:%M")


@router.message(F.text.in_(get_all_translations("btn_profile")))
async def show_profile(message: Message):
    """Показывает донаты пользователя и кнопку возврата, если он доступен."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    donations = await database.get_user_donations(user_id, 5)
    if len(donations) == 0:
        await message.answer(
            get_text(lang, "profile_title")
            + "\n\n"
            + get_text(lang, "profile_no_donations")
        )
        return

    total = await database.get_user_total(user_id)
    text = get_text(lang, "profile_title") + "\n\n"
    text = text + get_text(lang, "profile_total", total=total) + "\n\n"

    for donation in donations:
        line = (
            "⭐️ <b>"
            + str(donation["amount"])
            + "</b> ("
            + format_date(donation["created_at"])
            + ")"
        )
        if donation["refunded"] == 1:
            line = line + " " + get_text(lang, "refunded_label")
        if donation["message"] is not None and donation["message"] != "":
            line = line + "\n💬 <i>" + html.quote(donation["message"]) + "</i>"
        text = text + line + "\n"

    last_donation = await database.get_last_refundable_donation(user_id)
    refund_available = False
    if last_donation is not None:
        age = int(time.time()) - last_donation["created_at"]
        if age < REFUND_WINDOW_SECONDS:
            refund_available = True

    if refund_available:
        await message.answer(
            text,
            reply_markup=keyboards.request_refund_keyboard(lang),
        )
    else:
        await message.answer(text)
