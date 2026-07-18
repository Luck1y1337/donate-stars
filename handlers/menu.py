from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from config import ADMIN_ID
from locales import get_all_translations, get_text
from handlers import contact, donate, profile, start, stats

router = Router()


def is_admin(user_id):
    """Проверяет, что пользователь — админ."""
    return user_id == ADMIN_ID


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


async def show_hub(target, user_id):
    """Показывает инлайн-хаб со всеми разделами."""
    lang = await resolve_lang(user_id)
    await target.answer(
        get_text(lang, "hub_header"),
        reply_markup=keyboards.main_hub_keyboard(lang, is_admin(user_id)),
    )


@router.message(Command("menu"))
@router.message(F.text.in_(get_all_translations("btn_menu")))
async def cmd_menu(message: Message):
    """Команда /menu и кнопка-лаунчер «☰ Меню» — открывают хаб."""
    await show_hub(message, message.from_user.id)


@router.callback_query(F.data == "menu:donate")
async def hub_donate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await donate.open_donate(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:stats")
async def hub_stats(callback: CallbackQuery):
    await callback.answer()
    await stats.open_stats(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:profile")
async def hub_profile(callback: CallbackQuery):
    await callback.answer()
    await profile.open_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:contact")
async def hub_contact(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await contact.open_contact(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:help")
async def hub_help(callback: CallbackQuery):
    await callback.answer()
    await start.open_help(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:language")
async def hub_language(callback: CallbackQuery):
    await callback.answer()
    await start.open_language(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:admin")
async def hub_admin(callback: CallbackQuery, state: FSMContext):
    """Открывает админ-панель из хаба (только для админа)."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.answer()
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.answer(
        get_text(lang, "adm_panel_title"),
        reply_markup=keyboards.admin_panel_keyboard(lang),
    )
