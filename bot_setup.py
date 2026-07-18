import logging

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    MenuButtonCommands,
)

from config import ADMIN_ID
from locales import get_text

logger = logging.getLogger(__name__)

LANGS = ("ru", "uz", "en")

# Публичные команды: (команда, {язык: описание}). Показываются в меню команд.
PUBLIC_COMMANDS = [
    ("start", {"ru": "Запустить / выбрать язык", "en": "Start / choose language",
               "uz": "Boshlash / til tanlash"}),
    ("menu", {"ru": "Открыть меню", "en": "Open the menu",
              "uz": "Menyuni ochish"}),
    ("donate", {"ru": "Задонатить", "en": "Make a donation",
                "uz": "Donat qilish"}),
    ("stats", {"ru": "Статистика сбора", "en": "Fundraising stats",
               "uz": "Yig'ish statistikasi"}),
    ("profile", {"ru": "Мои донаты", "en": "My donations",
                 "uz": "Mening donatlarim"}),
    ("contact", {"ru": "Написать разработчику", "en": "Contact the developer",
                 "uz": "Dasturchiga yozish"}),
    ("help", {"ru": "Помощь", "en": "Help", "uz": "Yordam"}),
    ("language", {"ru": "Сменить язык", "en": "Change language",
                  "uz": "Tilni o'zgartirish"}),
    ("refund", {"ru": "Вернуть последний донат (24ч)",
                "en": "Refund your last donation (24h)",
                "uz": "Oxirgi donatni qaytarish (24s)"}),
]

# Дополнительные команды только для админа.
ADMIN_EXTRA_COMMANDS = [
    ("admin", {"ru": "Админ-панель", "en": "Admin panel",
               "uz": "Admin panel"}),
    ("setgoal", {"ru": "Установить цель сбора", "en": "Set the fundraising goal",
                 "uz": "Yig'ish maqsadini qo'yish"}),
    ("unblock", {"ru": "Разблокировать пользователя", "en": "Unblock a user",
                 "uz": "Foydalanuvchini blokdan chiqarish"}),
    ("backup", {"ru": "Бэкап базы сейчас", "en": "Backup the DB now",
                "uz": "Bazani zaxiralash"}),
    ("restore", {"ru": "Восстановить базу из файла",
                 "en": "Restore the DB from a file",
                 "uz": "Bazani fayldan tiklash"}),
]


def _commands(defs, lang):
    """Строит список BotCommand для языка (с запасным ru)."""
    result = []
    for command, descriptions in defs:
        description = descriptions.get(lang, descriptions["ru"])
        result.append(BotCommand(command=command, description=description))
    return result


async def setup_bot_profile(bot: Bot):
    """Регистрирует команды-подсказки, описания и кнопку меню.

    Всё обёрнуто в try/except: сбой Bot API не должен мешать запуску polling.
    """
    # Публичные подсказки команд: по языкам + запасной набор без кода языка.
    for lang in LANGS:
        try:
            await bot.set_my_commands(
                _commands(PUBLIC_COMMANDS, lang),
                scope=BotCommandScopeDefault(),
                language_code=lang,
            )
        except Exception as error:
            logger.warning("set_my_commands(%s) не удалось: %s", lang, error)
    try:
        await bot.set_my_commands(
            _commands(PUBLIC_COMMANDS, "ru"), scope=BotCommandScopeDefault()
        )
    except Exception as error:
        logger.warning("set_my_commands(default) не удалось: %s", error)

    # Админские подсказки: на чат админа, по языкам + запасной.
    admin_ids = [ADMIN_ID] if ADMIN_ID else []
    admin_defs = PUBLIC_COMMANDS + ADMIN_EXTRA_COMMANDS
    for admin_id in admin_ids:
        for lang in LANGS:
            try:
                await bot.set_my_commands(
                    _commands(admin_defs, lang),
                    scope=BotCommandScopeChat(chat_id=admin_id),
                    language_code=lang,
                )
            except Exception as error:
                logger.warning(
                    "admin set_my_commands(%s, %s) не удалось: %s",
                    admin_id, lang, error,
                )
        try:
            await bot.set_my_commands(
                _commands(admin_defs, "ru"),
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception as error:
            logger.warning(
                "admin set_my_commands(%s, default) не удалось: %s",
                admin_id, error,
            )

    # Многоязычное описание бота (видно до /start) и короткое описание (bio).
    for lang in LANGS:
        try:
            await bot.set_my_description(
                get_text(lang, "bot_description"), language_code=lang
            )
            await bot.set_my_short_description(
                get_text(lang, "bot_short_description"), language_code=lang
            )
        except Exception as error:
            logger.warning("set_my_description(%s) не удалось: %s", lang, error)

    # Синяя кнопка «Меню» показывает список команд.
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    except Exception as error:
        logger.warning("set_chat_menu_button не удалось: %s", error)
