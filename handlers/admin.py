import asyncio
import csv
import io
from datetime import datetime

from aiogram import F, Router, html
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

import database
import keyboards
from config import ADMIN_ID
from locales import get_all_translations, get_text
from states import AdminStates

router = Router()

router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)

DONATIONS_PAGE_SIZE = 8


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


def format_donor_name(username, user_id):
    """Возвращает безопасное отображаемое имя пользователя."""
    if username is not None:
        return "@" + html.quote(username)
    return "id " + str(user_id)


async def get_goal_numbers():
    """Возвращает (goal, cycle_start, total, collected)."""
    goal_value = await database.get_setting("goal_current")
    cycle_start_value = await database.get_setting("cycle_start_total")

    goal = 0
    if goal_value is not None:
        goal = int(goal_value)

    cycle_start = 0
    if cycle_start_value is not None:
        cycle_start = int(cycle_start_value)

    total = await database.get_total_all_time()
    collected = total - cycle_start
    if collected < 0:
        collected = 0

    return goal, cycle_start, total, collected


def build_donation_detail(lang, donation):
    """Собирает текст с деталями одного доната."""
    name = format_donor_name(donation["username"], donation["user_id"])
    text = "🧾 <b>#" + str(donation["id"]) + "</b>\n\n"
    text = text + get_text(
        lang, "adm_don_from", name=name, user_id=donation["user_id"]
    ) + "\n"
    text = text + get_text(
        lang, "adm_don_amount", amount=donation["amount"]
    ) + "\n"
    text = text + get_text(
        lang, "adm_don_date", date=format_date(donation["created_at"])
    ) + "\n"
    if donation["refunded"] == 1:
        text = text + get_text(lang, "adm_don_status_refunded")
    else:
        text = text + get_text(lang, "adm_don_status_active")
    if donation["message"] is not None and donation["message"] != "":
        safe_message = html.quote(donation["message"])
        text = text + "\n" + get_text(
            lang, "adm_don_message", message=safe_message
        )
    return text


async def do_admin_refund(bot, lang, donation_id):
    """Возвращает донат по id и уведомляет донатера. Возвращает текст ответа."""
    donation = await database.get_donation(donation_id)

    if donation is None:
        return get_text(lang, "adm_refund_not_found", id=donation_id)

    if donation["refunded"] == 1:
        return get_text(lang, "adm_refund_already", id=donation_id)

    try:
        await bot.refund_star_payment(
            user_id=donation["user_id"],
            telegram_payment_charge_id=donation["charge_id"],
        )
    except Exception as error:
        return get_text(
            lang, "adm_refund_failed", id=donation_id, error=str(error)
        )

    await database.mark_refunded(donation_id)

    donor_lang = await resolve_lang(donation["user_id"])
    try:
        await bot.send_message(
            donation["user_id"],
            get_text(donor_lang, "refund_by_admin", amount=donation["amount"]),
        )
    except Exception:
        pass

    return get_text(
        lang, "adm_refund_done", id=donation_id, amount=donation["amount"]
    )


@router.message(Command("admin"))
@router.message(F.text.in_(get_all_translations("btn_admin")))
async def open_admin_panel(message: Message, state: FSMContext):
    """Открывает админ-панель."""
    await state.clear()
    lang = await resolve_lang(message.from_user.id)
    await message.answer(
        get_text(lang, "adm_panel_title"),
        reply_markup=keyboards.admin_panel_keyboard(lang),
    )


@router.callback_query(F.data == "adm:home")
async def callback_admin_home(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню админ-панели."""
    await state.clear()
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_text(lang, "adm_panel_title"),
        reply_markup=keyboards.admin_panel_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:close")
async def callback_admin_close(callback: CallbackQuery, state: FSMContext):
    """Закрывает админ-панель."""
    await state.clear()
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "adm:noop")
async def callback_admin_noop(callback: CallbackQuery):
    """Заглушка для кнопки-счётчика страниц."""
    await callback.answer()


@router.callback_query(F.data == "adm:stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Показывает подробную статистику."""
    lang = await resolve_lang(callback.from_user.id)
    goal, cycle_start, total, collected = await get_goal_numbers()

    donations_count = await database.count_donations()
    donors_count = await database.count_donors()
    refunded_count = await database.count_refunded()
    users_count = await database.count_users()

    text = get_text(lang, "adm_stats_title") + "\n\n"
    text = text + get_text(lang, "adm_stats_users", count=users_count) + "\n"
    text = text + get_text(lang, "adm_stats_donors", count=donors_count) + "\n"
    text = text + get_text(
        lang, "adm_stats_donations", count=donations_count
    ) + "\n"
    text = text + get_text(
        lang, "adm_stats_refunds", count=refunded_count
    ) + "\n"
    text = text + get_text(lang, "adm_stats_total", total=total) + "\n\n"

    if goal > 0:
        percent = collected * 100 // goal
        if percent > 100:
            percent = 100
        text = text + get_text(lang, "adm_stats_goal_line", goal=goal) + "\n"
        text = text + get_text(
            lang, "adm_stats_cycle_line", collected=collected, percent=percent
        )
    else:
        text = text + get_text(lang, "adm_stats_no_goal")

    await callback.message.edit_text(
        text, reply_markup=keyboards.admin_back_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "adm:goal")
async def callback_admin_goal(callback: CallbackQuery):
    """Показывает управление целью сбора."""
    lang = await resolve_lang(callback.from_user.id)
    goal, cycle_start, total, collected = await get_goal_numbers()

    text = get_text(lang, "adm_goal_title") + "\n\n"
    if goal > 0:
        text = text + get_text(lang, "adm_goal_current", goal=goal) + "\n"
        text = text + get_text(lang, "adm_goal_collected", collected=collected)
    else:
        text = text + get_text(lang, "adm_goal_none")

    await callback.message.edit_text(
        text, reply_markup=keyboards.admin_goal_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "adm:goal:set")
async def callback_admin_goal_set(callback: CallbackQuery, state: FSMContext):
    """Просит ввести новую цель."""
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(AdminStates.waiting_goal)
    await callback.message.edit_text(
        get_text(lang, "adm_goal_enter"),
        reply_markup=keyboards.admin_back_keyboard(lang),
    )
    await callback.answer()


@router.message(AdminStates.waiting_goal)
async def process_admin_goal(message: Message, state: FSMContext):
    """Сохраняет новую цель."""
    lang = await resolve_lang(message.from_user.id)

    text = ""
    if message.text is not None:
        text = message.text.strip()

    if not text.isdigit() or int(text) <= 0:
        await message.answer(
            get_text(lang, "adm_goal_invalid"),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        return

    await state.clear()
    goal = int(text)
    await database.set_setting("goal_current", str(goal))
    await message.answer(
        get_text(lang, "adm_goal_set_ok", goal=goal),
        reply_markup=keyboards.admin_back_keyboard(lang),
    )


@router.callback_query(F.data == "adm:goal:reset")
async def callback_admin_goal_reset(callback: CallbackQuery):
    """Сбрасывает цель (устанавливает 0)."""
    lang = await resolve_lang(callback.from_user.id)
    await database.set_setting("goal_current", "0")
    await callback.message.edit_text(
        get_text(lang, "adm_goal_reset_ok"),
        reply_markup=keyboards.admin_goal_keyboard(lang),
    )
    await callback.answer()


async def render_donations_page(callback, lang, page):
    """Отрисовывает страницу списка донатов."""
    total_count = await database.count_all_donations()

    if total_count == 0:
        await callback.message.edit_text(
            get_text(lang, "adm_don_empty"),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        return

    total_pages = (total_count + DONATIONS_PAGE_SIZE - 1) // DONATIONS_PAGE_SIZE
    if page < 0:
        page = 0
    if page >= total_pages:
        page = total_pages - 1

    offset = page * DONATIONS_PAGE_SIZE
    donations = await database.get_donations_page(offset, DONATIONS_PAGE_SIZE)

    text = get_text(lang, "adm_don_title", count=total_count) + "\n\n"
    text = text + get_text(lang, "adm_don_hint")

    await callback.message.edit_text(
        text,
        reply_markup=keyboards.admin_donations_keyboard(
            lang, donations, page, total_pages
        ),
    )


@router.callback_query(F.data.startswith("adm:donations:"))
async def callback_admin_donations(callback: CallbackQuery):
    """Показывает список донатов с пагинацией."""
    lang = await resolve_lang(callback.from_user.id)
    page = int(callback.data.split(":")[2])
    await render_donations_page(callback, lang, page)
    await callback.answer()


@router.callback_query(F.data.startswith("adm:don:"))
async def callback_admin_donation_detail(callback: CallbackQuery):
    """Показывает детали одного доната."""
    lang = await resolve_lang(callback.from_user.id)
    parts = callback.data.split(":")
    donation_id = int(parts[2])
    page = int(parts[3])

    donation = await database.get_donation(donation_id)
    if donation is None:
        await callback.answer(
            get_text(lang, "adm_don_not_found"), show_alert=True
        )
        return

    await callback.message.edit_text(
        build_donation_detail(lang, donation),
        reply_markup=keyboards.admin_donation_detail_keyboard(
            lang, donation["id"], donation["refunded"], page
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:refund:"))
async def callback_admin_panel_refund(callback: CallbackQuery):
    """Возвращает донат из панели и обновляет детали."""
    lang = await resolve_lang(callback.from_user.id)
    parts = callback.data.split(":")
    donation_id = int(parts[2])
    page = int(parts[3])

    result = await do_admin_refund(callback.bot, lang, donation_id)
    await callback.answer(result, show_alert=True)

    donation = await database.get_donation(donation_id)
    if donation is None:
        await render_donations_page(callback, lang, page)
        return

    await callback.message.edit_text(
        build_donation_detail(lang, donation),
        reply_markup=keyboards.admin_donation_detail_keyboard(
            lang, donation["id"], donation["refunded"], page
        ),
    )


@router.callback_query(F.data == "adm:broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Просит ввести текст рассылки."""
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.edit_text(
        get_text(lang, "adm_bc_enter"),
        reply_markup=keyboards.admin_back_keyboard(lang),
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast)
async def process_admin_broadcast(message: Message, state: FSMContext):
    """Сохраняет текст рассылки и показывает подтверждение."""
    lang = await resolve_lang(message.from_user.id)

    if message.text is None or message.text.strip() == "":
        await message.answer(
            get_text(lang, "adm_bc_empty"),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        return

    await state.update_data(broadcast_text=message.text)
    users_count = await database.count_users()
    preview = html.quote(message.text)
    await message.answer(
        get_text(lang, "adm_bc_confirm", count=users_count, preview=preview),
        reply_markup=keyboards.admin_broadcast_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "adm:bc:send")
async def callback_admin_broadcast_send(callback: CallbackQuery,
                                        state: FSMContext):
    """Выполняет рассылку всем пользователям."""
    lang = await resolve_lang(callback.from_user.id)
    data = await state.get_data()
    text = data.get("broadcast_text")
    await state.clear()

    if text is None:
        await callback.message.edit_text(
            get_text(lang, "adm_bc_lost"),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        await callback.answer()
        return

    await callback.message.edit_text(get_text(lang, "adm_bc_started"))
    await callback.answer()

    user_ids = await database.get_all_user_ids()
    sent = 0
    failed = 0
    for user_id in user_ids:
        try:
            await callback.bot.send_message(user_id, text, parse_mode=None)
            sent = sent + 1
        except Exception:
            failed = failed + 1
        await asyncio.sleep(0.05)

    await callback.message.answer(
        get_text(lang, "adm_bc_done", sent=sent, failed=failed),
        reply_markup=keyboards.admin_back_keyboard(lang),
    )


@router.callback_query(F.data == "adm:export")
async def callback_admin_export(callback: CallbackQuery):
    """Экспортирует все донаты в CSV-файл."""
    lang = await resolve_lang(callback.from_user.id)
    donations = await database.get_all_donations()

    if len(donations) == 0:
        await callback.answer(
            get_text(lang, "adm_export_empty"), show_alert=True
        )
        return

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "user_id",
            "username",
            "amount",
            "message",
            "charge_id",
            "refunded",
            "created_at",
        ]
    )
    for donation in donations:
        message_value = ""
        if donation["message"] is not None:
            message_value = donation["message"]
        writer.writerow(
            [
                donation["id"],
                donation["user_id"],
                donation["username"],
                donation["amount"],
                message_value,
                donation["charge_id"],
                donation["refunded"],
                format_date(donation["created_at"]),
            ]
        )

    data_bytes = buffer.getvalue().encode("utf-8-sig")
    file_name = "donations_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv"
    document = BufferedInputFile(data_bytes, filename=file_name)

    await callback.message.answer_document(
        document,
        caption=get_text(lang, "adm_export_caption", count=len(donations)),
    )
    await callback.answer()


@router.callback_query(F.data == "adm:search")
async def callback_admin_search(callback: CallbackQuery, state: FSMContext):
    """Просит ввести запрос для поиска донатов."""
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(AdminStates.waiting_search)
    await callback.message.edit_text(
        get_text(lang, "adm_search_enter"),
        reply_markup=keyboards.admin_back_keyboard(lang),
    )
    await callback.answer()


@router.message(AdminStates.waiting_search)
async def process_admin_search(message: Message, state: FSMContext):
    """Ищет донаты по запросу и показывает результат."""
    lang = await resolve_lang(message.from_user.id)

    query = ""
    if message.text is not None:
        query = message.text.strip()

    if query == "":
        await message.answer(
            get_text(lang, "adm_search_empty"),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        return

    await state.clear()
    donations = await database.find_donations(query)
    safe_query = html.quote(query)

    if len(donations) == 0:
        await message.answer(
            get_text(lang, "adm_search_none", query=safe_query),
            reply_markup=keyboards.admin_back_keyboard(lang),
        )
        return

    text = get_text(lang, "adm_search_found", count=len(donations)) + "\n\n"
    for donation in donations:
        name = format_donor_name(donation["username"], donation["user_id"])
        line = (
            "🧾 <b>#"
            + str(donation["id"])
            + "</b> — "
            + name
            + " — <b>"
            + str(donation["amount"])
            + "⭐️</b> ("
            + format_date(donation["created_at"])
            + ")"
        )
        if donation["refunded"] == 1:
            line = line + " " + get_text(lang, "adm_search_refunded_tag")
        if donation["message"] is not None and donation["message"] != "":
            line = line + "\n💬 " + html.quote(donation["message"])
        text = text + line + "\n"

    await message.answer(
        text, reply_markup=keyboards.admin_back_keyboard(lang)
    )


@router.message(Command("setgoal"))
async def cmd_setgoal(message: Message, command: CommandObject):
    """Устанавливает новую цель сбора."""
    lang = await resolve_lang(message.from_user.id)

    if command.args is None or not command.args.strip().isdigit():
        await message.answer(get_text(lang, "adm_setgoal_usage"))
        return

    goal = int(command.args.strip())
    if goal <= 0:
        await message.answer(get_text(lang, "adm_setgoal_positive"))
        return

    await database.set_setting("goal_current", str(goal))
    await message.answer(get_text(lang, "adm_goal_set_ok", goal=goal))


@router.message(Command("refund"))
async def cmd_admin_refund(message: Message, command: CommandObject):
    """Возвращает донат по id (без ограничения по времени)."""
    lang = await resolve_lang(message.from_user.id)

    if command.args is None or not command.args.strip().isdigit():
        await message.answer(get_text(lang, "adm_refund_usage"))
        return

    donation_id = int(command.args.strip())
    result = await do_admin_refund(message.bot, lang, donation_id)
    await message.answer(result)


@router.callback_query(F.data.startswith("admin_refund:"))
async def callback_admin_refund(callback: CallbackQuery):
    """Возвращает донат по кнопке в уведомлении о донате."""
    lang = await resolve_lang(callback.from_user.id)
    donation_id = int(callback.data.split(":")[1])
    result = await do_admin_refund(callback.bot, lang, donation_id)
    await callback.message.answer(result)
    await callback.answer()
