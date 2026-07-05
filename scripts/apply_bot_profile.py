"""
Applies the bot's public presentation (name, about, description and command
menus) to Telegram via the Bot API. Safe to re-run at any time.

Usage:
    venv/Scripts/python.exe scripts/apply_bot_profile.py
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ADMIN_ID, BOT_TOKEN

API = "https://api.telegram.org/bot" + BOT_TOKEN + "/"


def call(method, payload):
    """Вызывает метод Bot API и возвращает результат JSON."""
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API + method,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        body = json.loads(response.read().decode("utf-8"))
    if not body.get("ok"):
        print("  FAILED:", method, body)
    return body


# Short description — shown under the bot name on its profile (max 120 chars).
SHORT = {
    "en": "Support @utofi with Telegram Stars. Donations, a goal, stats & refunds.",
    "ru": "Поддержка @utofi звёздами Telegram. Донаты, цель сбора, статистика.",
    "uz": "@utofi'ni Telegram yulduzlari bilan qo'llash. Donatlar va statistika.",
}

# Description — shown on the empty chat screen before Start (max 512 chars).
DESCRIPTION = {
    "en": (
        "This is the support bot for developer @utofi.\n\n"
        "Send a donation with Telegram Stars, track the fundraising goal and "
        "public stats, and refund within 24 hours if needed.\n\n"
        "Press Start, choose a language and support the project."
    ),
    "ru": (
        "Это бот поддержки разработчика @utofi.\n\n"
        "Отправьте донат звёздами Telegram, следите за целью сбора и "
        "статистикой, а при необходимости верните донат в течение 24 часов.\n\n"
        "Нажмите «Start», выберите язык и поддержите проект."
    ),
    "uz": (
        "Bu dasturchi @utofi uchun qo'llab-quvvatlash boti.\n\n"
        "Telegram yulduzlari bilan donat yuboring, maqsad va statistikani "
        "kuzating, kerak bo'lsa 24 soat ichida qaytaring.\n\n"
        "«Start» tugmasini bosing, tilni tanlang va loyihani qo'llang."
    ),
}

# Public command menu.
COMMANDS = {
    "en": [
        ("start", "Start the bot / choose language"),
        ("donate", "Make a donation"),
        ("stats", "Stats & fundraising goal"),
        ("refund", "Refund your last donation"),
        ("help", "Help"),
    ],
    "ru": [
        ("start", "Запустить бота / выбрать язык"),
        ("donate", "Задонатить"),
        ("stats", "Статистика и цель сбора"),
        ("refund", "Вернуть последний донат"),
        ("help", "Помощь"),
    ],
    "uz": [
        ("start", "Botni ishga tushirish / til tanlash"),
        ("donate", "Donat qilish"),
        ("stats", "Statistika va maqsad"),
        ("refund", "Oxirgi donatni qaytarish"),
        ("help", "Yordam"),
    ],
}

# Extended command menu shown only to the admin (adds admin commands).
ADMIN_COMMANDS = [
    ("start", "Запустить бота / выбрать язык"),
    ("donate", "Задонатить"),
    ("stats", "Статистика и цель сбора"),
    ("admin", "Админ-панель"),
    ("setgoal", "Установить цель сбора"),
    ("refund", "Вернуть донат по id"),
    ("help", "Помощь"),
]


def to_command_list(pairs):
    """Преобразует пары (command, description) в формат Bot API."""
    result = []
    for command, description in pairs:
        result.append({"command": command, "description": description})
    return result


def main():
    if BOT_TOKEN == "":
        print("BOT_TOKEN is empty. Fill in .env first.")
        return

    print("Setting bot name...")
    call("setMyName", {"name": "Support Luck1y🍀"})

    for lang in ["en", "ru", "uz"]:
        print("Applying locale:", lang)
        # Default (no language_code) uses English as a neutral fallback.
        if lang == "en":
            call("setMyShortDescription", {"short_description": SHORT["en"]})
            call("setMyDescription", {"description": DESCRIPTION["en"]})
            call("setMyCommands", {"commands": to_command_list(COMMANDS["en"])})

        call("setMyShortDescription", {
            "short_description": SHORT[lang],
            "language_code": lang,
        })
        call("setMyDescription", {
            "description": DESCRIPTION[lang],
            "language_code": lang,
        })
        call("setMyCommands", {
            "commands": to_command_list(COMMANDS[lang]),
            "language_code": lang,
        })

    if ADMIN_ID and ADMIN_ID != 0:
        print("Applying admin command menu for chat", ADMIN_ID)
        call("setMyCommands", {
            "commands": to_command_list(ADMIN_COMMANDS),
            "scope": {"type": "chat", "chat_id": ADMIN_ID},
        })

    print("Done.")


if __name__ == "__main__":
    main()
