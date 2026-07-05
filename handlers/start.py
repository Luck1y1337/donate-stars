from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from config import ADMIN_ID
from locales import get_all_translations, get_text

router = Router()


def is_admin(user_id):
    """Проверяет, что пользователь — админ."""
    if user_id == ADMIN_ID:
        return True
    return False


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return "ru"
    return lang


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Регистрирует пользователя и показывает выбор языка или меню."""
    user_id = message.from_user.id
    username = message.from_user.username
    await database.add_user(user_id, username)

    lang = await database.get_user_lang(user_id)
    if lang is None:
        await message.answer(
            get_text("ru", "choose_language"),
            reply_markup=keyboards.language_keyboard(),
        )
    else:
        name = html.quote(message.from_user.first_name)
        await message.answer(
            get_text(lang, "welcome", name=name),
            reply_markup=keyboards.main_menu_keyboard(
                lang, is_admin(user_id)
            ),
        )


@router.callback_query(F.data.startswith("lang:"))
async def callback_choose_language(callback: CallbackQuery):
    """Сохраняет выбранный язык и показывает главное меню."""
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username

    await database.add_user(user_id, username)
    await database.set_user_lang(user_id, lang)

    name = html.quote(callback.from_user.first_name)
    await callback.message.delete()
    await callback.message.answer(
        get_text(lang, "welcome", name=name),
        reply_markup=keyboards.main_menu_keyboard(lang, is_admin(user_id)),
    )
    await callback.answer()


@router.message(F.text.in_(get_all_translations("btn_language")))
async def button_language(message: Message):
    """Показывает выбор языка по кнопке меню."""
    lang = await resolve_lang(message.from_user.id)
    await message.answer(
        get_text(lang, "choose_language"),
        reply_markup=keyboards.language_keyboard(),
    )


@router.message(Command("help"))
@router.message(F.text.in_(get_all_translations("btn_help")))
async def button_help(message: Message):
    """Показывает справку по разделам меню."""
    lang = await resolve_lang(message.from_user.id)
    await message.answer(get_text(lang, "help_text"))


@router.callback_query(F.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Закрывает инлайн-шаг и возвращает в главное меню."""
    await state.clear()
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(get_text(lang, "main_menu"))
    await callback.answer()
