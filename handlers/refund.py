import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from config import REFUND_WINDOW_SECONDS
from locales import get_text

router = Router()


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


def is_within_refund_window(donation):
    """Проверяет, что донат моложе 24 часов."""
    age = int(time.time()) - donation["created_at"]
    if age < REFUND_WINDOW_SECONDS:
        return True
    return False


async def start_refund_flow(user_id, lang, answer_func):
    """Находит последний донат и просит подтвердить возврат."""
    donation = await database.get_last_refundable_donation(user_id)

    if donation is None:
        await answer_func(get_text(lang, "refund_nothing"))
        return

    if not is_within_refund_window(donation):
        await answer_func(get_text(lang, "refund_too_late"))
        return

    await answer_func(
        get_text(lang, "refund_confirm", amount=donation["amount"]),
        reply_markup=keyboards.refund_confirm_keyboard(lang, donation["id"]),
    )


@router.message(Command("refund"))
async def cmd_refund(message: Message):
    """Запускает возврат последнего доната по команде."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)
    await start_refund_flow(user_id, lang, message.answer)


@router.callback_query(F.data == "refund:request")
async def callback_refund_request(callback: CallbackQuery):
    """Запускает возврат по кнопке в профиле."""
    user_id = callback.from_user.id
    lang = await resolve_lang(user_id)
    await start_refund_flow(user_id, lang, callback.message.answer)
    await callback.answer()


@router.callback_query(F.data.startswith("refund:yes:"))
async def callback_refund_confirm(callback: CallbackQuery):
    """Выполняет возврат после подтверждения."""
    user_id = callback.from_user.id
    lang = await resolve_lang(user_id)
    donation_id = int(callback.data.split(":")[2])

    donation = await database.get_donation(donation_id)

    if donation is None:
        await callback.message.edit_text(get_text(lang, "refund_nothing"))
        await callback.answer()
        return

    if donation["user_id"] != user_id:
        await callback.answer()
        return

    if donation["refunded"] == 1:
        await callback.message.edit_text(get_text(lang, "refund_nothing"))
        await callback.answer()
        return

    if not is_within_refund_window(donation):
        await callback.message.edit_text(get_text(lang, "refund_too_late"))
        await callback.answer()
        return

    await callback.bot.refund_star_payment(
        user_id=user_id,
        telegram_payment_charge_id=donation["charge_id"],
    )
    await database.mark_refunded(donation_id)

    await callback.message.edit_text(
        get_text(lang, "refund_done", amount=donation["amount"])
    )
    await callback.answer()


@router.callback_query(F.data == "refund:no")
async def callback_refund_cancel(callback: CallbackQuery):
    """Отменяет возврат."""
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(get_text(lang, "refund_cancelled"))
    await callback.answer()
