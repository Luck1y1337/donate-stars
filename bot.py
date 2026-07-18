import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import database
import scheduler
from bot_setup import setup_bot_profile
from config import BOT_TOKEN
from handlers import (
    admin,
    contact,
    donate,
    menu,
    profile,
    refund,
    start,
    stats,
)


async def main():
    """Точка входа: инициализирует базу и запускает polling."""
    # Explicit stdout stream: hosting dashboards (e.g. Railway) color log
    # lines by stream, not by level, so stderr shows everything as red.
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )

    if BOT_TOKEN == "":
        print("Ошибка: BOT_TOKEN не задан. Заполните файл .env.")
        return

    await database.init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(donate.router)
    dp.include_router(contact.router)
    dp.include_router(stats.router)
    dp.include_router(profile.router)
    dp.include_router(refund.router)

    scheduler.start_scheduler(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await setup_bot_profile(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
