import time

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)

import database
import keyboards
from config import (
    ADMIN_ID,
    MAX_DONATE_AMOUNT,
    MIN_DONATE_AMOUNT,
    THANK_YOU_STICKER_ID,
)
from locales import get_all_translations, get_text
from states import DonateStates

router = Router()


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


async def send_donation_invoice(bot, chat_id, lang, amount):
    """Отправляет инвойс на оплату в Telegram Stars."""
    payload = "donate_" + str(chat_id) + "_" + str(int(time.time()))
    price = LabeledPrice(
        label=get_text(lang, "invoice_title"),
        amount=amount,
    )
    await bot.send_invoice(
        chat_id=chat_id,
        title=get_text(lang, "invoice_title"),
        description=get_text(lang, "invoice_description", amount=amount),
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[price],
    )


@router.message(Command("donate"))
@router.message(F.text.in_(get_all_translations("btn_donate")))
async def button_donate(message: Message, state: FSMContext):
    """Открывает выбор суммы доната."""
    await state.clear()
    lang = await resolve_lang(message.from_user.id)
    await message.answer(
        get_text(lang, "choose_amount"),
        reply_markup=keyboards.amounts_keyboard(lang),
    )


@router.callback_query(F.data == "donate:open")
async def callback_open_amounts(callback: CallbackQuery, state: FSMContext):
    """Возвращает к выбору суммы (кнопка «Назад»)."""
    await state.clear()
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "choose_amount"),
        reply_markup=keyboards.amounts_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("donate:amt:"))
async def callback_choose_amount(callback: CallbackQuery, state: FSMContext):
    """Сохраняет выбранную сумму и спрашивает про комментарий."""
    amount = int(callback.data.split(":")[2])
    await state.update_data(amount=amount)
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "ask_comment", amount=amount),
        reply_markup=keyboards.comment_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "donate:custom")
async def callback_custom_amount(callback: CallbackQuery, state: FSMContext):
    """Просит ввести свою сумму доната."""
    await state.set_state(DonateStates.waiting_custom_amount)
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_text(
            lang,
            "enter_custom_amount",
            min_amount=MIN_DONATE_AMOUNT,
            max_amount=MAX_DONATE_AMOUNT,
        ),
        reply_markup=keyboards.back_to_amounts_keyboard(lang),
    )
    await callback.answer()


@router.message(DonateStates.waiting_custom_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    """Проверяет введённую сумму и спрашивает про комментарий."""
    lang = await resolve_lang(message.from_user.id)

    text = ""
    if message.text is not None:
        text = message.text.strip()

    if not text.isdigit():
        await message.answer(
            get_text(
                lang,
                "invalid_amount",
                min_amount=MIN_DONATE_AMOUNT,
                max_amount=MAX_DONATE_AMOUNT,
            ),
            reply_markup=keyboards.back_to_amounts_keyboard(lang),
        )
        return

    amount = int(text)
    if amount < MIN_DONATE_AMOUNT or amount > MAX_DONATE_AMOUNT:
        await message.answer(
            get_text(
                lang,
                "invalid_amount",
                min_amount=MIN_DONATE_AMOUNT,
                max_amount=MAX_DONATE_AMOUNT,
            ),
            reply_markup=keyboards.back_to_amounts_keyboard(lang),
        )
        return

    await state.set_state(None)
    await state.update_data(amount=amount)
    await message.answer(
        get_text(lang, "ask_comment", amount=amount),
        reply_markup=keyboards.comment_keyboard(lang),
    )


@router.callback_query(F.data == "comment:ask")
async def callback_back_to_comment(callback: CallbackQuery, state: FSMContext):
    """Возвращает к вопросу про комментарий (кнопка «Назад»)."""
    await state.set_state(None)
    data = await state.get_data()
    amount = data.get("amount")
    lang = await resolve_lang(callback.from_user.id)

    if amount is None:
        await callback.message.edit_text(
            get_text(lang, "choose_amount"),
            reply_markup=keyboards.amounts_keyboard(lang),
        )
    else:
        await callback.message.edit_text(
            get_text(lang, "ask_comment", amount=amount),
            reply_markup=keyboards.comment_keyboard(lang),
        )
    await callback.answer()


@router.callback_query(F.data == "comment:write")
async def callback_write_comment(callback: CallbackQuery, state: FSMContext):
    """Просит ввести текст комментария к донату."""
    await state.set_state(DonateStates.waiting_comment)
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "enter_comment"),
        reply_markup=keyboards.back_to_comment_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "comment:skip")
async def callback_skip_comment(callback: CallbackQuery, state: FSMContext):
    """Отправляет инвойс без комментария."""
    data = await state.get_data()
    amount = data.get("amount")
    lang = await resolve_lang(callback.from_user.id)

    if amount is None:
        await callback.message.edit_text(
            get_text(lang, "choose_amount"),
            reply_markup=keyboards.amounts_keyboard(lang),
        )
        await callback.answer()
        return

    await state.set_state(None)
    await state.update_data(donate_message=None)
    await callback.message.delete()
    await send_donation_invoice(
        callback.bot, callback.from_user.id, lang, amount
    )
    await callback.answer()


@router.message(DonateStates.waiting_comment)
async def process_comment(message: Message, state: FSMContext):
    """Сохраняет комментарий и отправляет инвойс."""
    data = await state.get_data()
    amount = data.get("amount")
    lang = await resolve_lang(message.from_user.id)

    if amount is None:
        await state.clear()
        await message.answer(
            get_text(lang, "choose_amount"),
            reply_markup=keyboards.amounts_keyboard(lang),
        )
        return

    await state.set_state(None)
    await state.update_data(donate_message=message.text)
    await send_donation_invoice(message.bot, message.from_user.id, lang, amount)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Подтверждает оплату перед списанием звёзд."""
    await pre_checkout_query.answer(ok=True)


async def check_goal_reached(bot):
    """Проверяет прогресс цели и уведомляет админа о её достижении."""
    goal_value = await database.get_setting("goal_current")
    cycle_start_value = await database.get_setting("cycle_start_total")

    goal = 0
    if goal_value is not None:
        goal = int(goal_value)

    cycle_start = 0
    if cycle_start_value is not None:
        cycle_start = int(cycle_start_value)

    if goal <= 0:
        return

    total = await database.get_total_all_time()
    collected = total - cycle_start

    if collected >= goal:
        await database.set_setting("cycle_start_total", str(total))
        await database.set_setting("goal_current", "0")
        await bot.send_message(
            ADMIN_ID,
            "🎯 Цель " + str(goal) + "⭐️ достигнута! "
            "Установите новую командой /setgoal <число>.",
        )


async def notify_admin_about_donation(bot, donation_id, username, user_id,
                                      amount, comment):
    """Отправляет админу уведомление о новом донате."""
    admin_lang = await resolve_lang(ADMIN_ID)

    if username is not None:
        user_label = "@" + html.quote(username)
    else:
        user_label = "id " + str(user_id)

    text = get_text(admin_lang, "adm_new_donation_title", id=donation_id) + "\n\n"
    text = text + get_text(
        admin_lang, "adm_don_from", name=user_label, user_id=user_id
    ) + "\n"
    text = text + get_text(admin_lang, "adm_don_amount", amount=amount)
    if comment is not None and comment != "":
        safe_comment = html.quote(comment)
        text = text + "\n" + get_text(
            admin_lang, "adm_don_message", message=safe_comment
        )

    await bot.send_message(
        ADMIN_ID,
        text,
        reply_markup=keyboards.admin_refund_keyboard(admin_lang, donation_id),
    )


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    """Сохраняет донат, благодарит донатера и уведомляет админа."""
    user_id = message.from_user.id
    username = message.from_user.username
    amount = message.successful_payment.total_amount
    charge_id = message.successful_payment.telegram_payment_charge_id

    data = await state.get_data()
    comment = data.get("donate_message")
    await state.clear()

    donation_id = await database.add_donation(
        user_id, username, amount, comment, charge_id
    )

    lang = await resolve_lang(user_id)
    await message.answer(get_text(lang, "thank_you", amount=amount))

    if THANK_YOU_STICKER_ID != "":
        try:
            await message.answer_sticker(THANK_YOU_STICKER_ID)
        except Exception:
            pass

    await check_goal_reached(message.bot)
    await notify_admin_about_donation(
        message.bot, donation_id, username, user_id, amount, comment
    )
