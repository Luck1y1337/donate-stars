import time

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from config import ADMIN_ID
from locales import get_all_translations, get_text
from states import ContactStates

router = Router()

CONTACT_COOLDOWN_SECONDS = 45

SUPPORTED_CONTENT_TYPES = {
    "text",
    "photo",
    "voice",
    "video",
    "document",
    "sticker",
}


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


async def open_contact(target, user_id, state):
    """Начинает диалог отправки сообщения разработчику.

    Общее ядро для команды и инлайн-хаба.
    """
    lang = await resolve_lang(user_id)

    is_blocked = await database.is_user_blocked(user_id)
    if is_blocked:
        await target.answer(get_text(lang, "contact_blocked"))
        return

    await state.set_state(ContactStates.waiting_message)
    await target.answer(
        get_text(lang, "contact_enter_message"),
        reply_markup=keyboards.contact_user_cancel_keyboard(lang),
    )


@router.message(Command("contact"))
@router.message(F.text.in_(get_all_translations("btn_contact")))
async def button_contact(message: Message, state: FSMContext):
    """Команда /contact и кнопка меню — начинают сообщение разработчику."""
    await open_contact(message, message.from_user.id, state)


@router.callback_query(F.data == "contact:cancel")
async def callback_contact_cancel(callback: CallbackQuery, state: FSMContext):
    """Отменяет ввод сообщения пользователем."""
    lang = await resolve_lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text(lang, "contact_cancelled"))
    await callback.answer()


@router.message(ContactStates.waiting_message,
                F.content_type.in_(SUPPORTED_CONTENT_TYPES))
async def process_contact_message(message: Message, state: FSMContext):
    """Принимает сообщение пользователя и пересылает его админу."""
    lang = await resolve_lang(message.from_user.id)

    is_blocked = await database.is_user_blocked(message.from_user.id)
    if is_blocked:
        await state.clear()
        await message.answer(get_text(lang, "contact_blocked"))
        return

    last_time = await database.get_last_contact_message_time(
        message.from_user.id, "to_admin"
    )
    now = int(time.time())
    if last_time is not None:
        elapsed = now - last_time
        if elapsed < CONTACT_COOLDOWN_SECONDS:
            remaining = CONTACT_COOLDOWN_SECONDS - elapsed
            await message.answer(
                get_text(lang, "contact_cooldown", seconds=remaining)
            )
            return

    admin_lang = await resolve_lang(ADMIN_ID)
    if message.from_user.username is not None:
        header = get_text(
            admin_lang,
            "contact_header_admin_named",
            username=html.quote(message.from_user.username),
            user_id=message.from_user.id,
        )
    else:
        header = get_text(
            admin_lang, "contact_header_admin_noname", user_id=message.from_user.id
        )

    await message.bot.send_message(ADMIN_ID, header)
    await message.copy_to(
        ADMIN_ID,
        reply_markup=keyboards.contact_admin_notify_keyboard(
            admin_lang, message.from_user.id
        ),
    )

    await database.add_contact_message(
        message.from_user.id,
        "to_admin",
        message.content_type,
        message.chat.id,
        message.message_id,
    )

    await state.clear()
    await message.answer(get_text(lang, "contact_sent_confirmation"))


@router.message(ContactStates.waiting_message)
async def process_contact_unsupported(message: Message):
    """Отклоняет неподдерживаемые типы сообщений на шаге ввода."""
    lang = await resolve_lang(message.from_user.id)
    await message.answer(get_text(lang, "contact_unsupported_type"))
