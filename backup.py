import os
import zipfile

from aiogram import Bot
from aiogram.types import FSInputFile

import database
from config import ADMIN_ID


async def perform_backup(bot: Bot):
    """Делает снимок БД, пакует в zip и присылает админу в личку."""
    if not ADMIN_ID:
        return

    os.makedirs("cache/backup", exist_ok=True)
    snapshot = "cache/backup/snapshot.db"
    zip_path = "cache/backup/backup.zip"

    try:
        # Консистентный снимок через online backup API; dest не должен существовать.
        if os.path.exists(snapshot):
            os.remove(snapshot)
        await database.backup_to(snapshot)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(snapshot, "bot.db")

        os.remove(snapshot)
        await bot.send_document(
            ADMIN_ID,
            FSInputFile(zip_path, filename="stars_backup.zip"),
            caption=(
                "📦 Автоматический бэкап базы данных.\n\n"
                "Чтобы восстановить: перешли этот файл боту с подписью "
                "<code>/restore</code>."
            ),
        )
    except Exception as error:
        try:
            await bot.send_message(
                ADMIN_ID, "⚠️ Ошибка при создании авто-бэкапа: " + str(error)
            )
        except Exception:
            pass
