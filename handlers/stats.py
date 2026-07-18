from datetime import datetime

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.types import Message

import database
from locales import get_all_translations, get_text

router = Router()

MEDALS = ["🥇", "🥈", "🥉"]


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


def build_progress_bar(percent):
    """Строит текстовый прогресс-бар из 10 блоков."""
    filled = percent // 10
    if filled > 10:
        filled = 10
    empty = 10 - filled
    return "█" * filled + "░" * empty


def format_donor_name(username, user_id):
    """Возвращает безопасное отображаемое имя донатера."""
    if username is not None:
        return "@" + html.quote(username)
    return "user " + str(user_id)


async def build_goal_block(lang):
    """Собирает блок с прогрессом цели."""
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

    if goal <= 0:
        bar = build_progress_bar(100)
        return bar + " 100%\n" + get_text(lang, "goal_waiting")

    percent = collected * 100 // goal
    if percent > 100:
        percent = 100

    bar = build_progress_bar(percent)
    progress_text = get_text(
        lang, "goal_progress", collected=collected, goal=goal
    )
    return progress_text + "\n" + bar + " " + str(percent) + "%"


async def open_stats(target, user_id):
    """Показывает прогресс цели, топ донатеров и последние донаты.

    Общее ядро для команды и инлайн-хаба.
    """
    lang = await resolve_lang(user_id)

    goal_block = await build_goal_block(lang)
    text = get_text(lang, "stats_title") + "\n\n" + goal_block

    top_donors = await database.get_top_donors(5)
    if len(top_donors) == 0:
        text = text + "\n\n" + get_text(lang, "no_donations")
        await target.answer(text)
        return

    text = text + "\n\n" + get_text(lang, "top_donors") + "\n"
    place = 0
    for donor in top_donors:
        place = place + 1
        if place <= 3:
            prefix = MEDALS[place - 1]
        else:
            prefix = str(place) + "."
        name = format_donor_name(donor["username"], donor["user_id"])
        text = (
            text
            + prefix
            + " "
            + name
            + " — <b>"
            + str(donor["total"])
            + "⭐️</b>\n"
        )

    recent = await database.get_recent_donations(5)
    if len(recent) > 0:
        text = text + "\n" + get_text(lang, "recent_donations") + "\n"
        for donation in recent:
            name = format_donor_name(
                donation["username"], donation["user_id"]
            )
            line = (
                name
                + " — <b>"
                + str(donation["amount"])
                + "⭐️</b> ("
                + format_date(donation["created_at"])
                + ")"
            )
            if donation["message"] is not None and donation["message"] != "":
                line = line + "\n💬 <i>" + html.quote(donation["message"]) + "</i>"
            text = text + line + "\n"

    await target.answer(text)


@router.message(Command("stats"))
@router.message(F.text.in_(get_all_translations("btn_stats")))
async def show_stats(message: Message):
    """Команда /stats и кнопка меню — показывают статистику."""
    await open_stats(message, message.from_user.id)
