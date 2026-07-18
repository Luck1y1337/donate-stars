import time

import aiosqlite

from config import DB_PATH


async def init_db():
    """Создаёт таблицы и настройки по умолчанию, если их ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "user_id INTEGER PRIMARY KEY, "
            "username TEXT, "
            "lang TEXT, "
            "created_at INTEGER, "
            "is_blocked INTEGER DEFAULT 0)"
        )
        try:
            await db.execute(
                "ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0"
            )
            await db.commit()
        except Exception:
            pass
        await db.execute(
            "CREATE TABLE IF NOT EXISTS contact_messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, "
            "direction TEXT, "
            "content_type TEXT, "
            "from_chat_id INTEGER, "
            "message_id INTEGER, "
            "created_at INTEGER)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS donations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, "
            "username TEXT, "
            "amount INTEGER, "
            "message TEXT, "
            "charge_id TEXT, "
            "refunded INTEGER DEFAULT 0, "
            "created_at INTEGER)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS settings ("
            "key TEXT PRIMARY KEY, "
            "value TEXT)"
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('goal_current', '0')"
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('cycle_start_total', '0')"
        )
        await db.commit()


async def get_user(user_id):
    """Возвращает строку пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row


async def add_user(user_id, username):
    """Добавляет пользователя, если его ещё нет, и обновляет username."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, lang, created_at) "
            "VALUES (?, ?, NULL, ?)",
            (user_id, username, now),
        )
        await db.execute(
            "UPDATE users SET username = ? WHERE user_id = ?",
            (username, user_id),
        )
        await db.commit()


async def set_user_lang(user_id, lang):
    """Сохраняет выбранный язык пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET lang = ? WHERE user_id = ?",
            (lang, user_id),
        )
        await db.commit()


async def get_user_lang(user_id):
    """Возвращает язык пользователя или None, если язык не выбран."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT lang FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def add_donation(user_id, username, amount, message, charge_id):
    """Сохраняет донат и возвращает его id."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO donations "
            "(user_id, username, amount, message, charge_id, refunded, created_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?)",
            (user_id, username, amount, message, charge_id, now),
        )
        await db.commit()
        return cursor.lastrowid


async def get_donation(donation_id):
    """Возвращает донат по id или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM donations WHERE id = ?", (donation_id,)
        )
        row = await cursor.fetchone()
        return row


async def mark_refunded(donation_id):
    """Помечает донат как возвращённый."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE donations SET refunded = 1 WHERE id = ?", (donation_id,)
        )
        await db.commit()


async def get_total_all_time():
    """Возвращает сумму всех невозвращённых донатов."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM donations WHERE refunded = 0"
        )
        row = await cursor.fetchone()
        return row[0]


async def get_top_donors(limit):
    """Возвращает топ донатеров: (user_id, username, total)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT user_id, username, SUM(amount) AS total "
            "FROM donations WHERE refunded = 0 "
            "GROUP BY user_id ORDER BY total DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return rows


async def get_recent_donations(limit):
    """Возвращает последние невозвращённые донаты."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM donations WHERE refunded = 0 "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return rows


async def get_user_total(user_id):
    """Возвращает сумму невозвращённых донатов пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM donations "
            "WHERE user_id = ? AND refunded = 0",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0]


async def get_user_donations(user_id, limit):
    """Возвращает последние донаты пользователя (включая возвращённые)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM donations WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return rows


async def get_last_refundable_donation(user_id):
    """Возвращает последний невозвращённый донат пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM donations WHERE user_id = ? AND refunded = 0 "
            "ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row


async def count_users():
    """Возвращает количество пользователей бота."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]


async def get_all_user_ids():
    """Возвращает список всех user_id для рассылки."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
        return result


async def count_donations():
    """Возвращает количество невозвращённых донатов."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM donations WHERE refunded = 0"
        )
        row = await cursor.fetchone()
        return row[0]


async def count_donors():
    """Возвращает количество уникальных донатеров."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM donations WHERE refunded = 0"
        )
        row = await cursor.fetchone()
        return row[0]


async def count_refunded():
    """Возвращает количество возвращённых донатов."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM donations WHERE refunded = 1"
        )
        row = await cursor.fetchone()
        return row[0]


async def count_all_donations():
    """Возвращает общее число донатов (включая возвраты) для пагинации."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM donations")
        row = await cursor.fetchone()
        return row[0]


async def get_donations_page(offset, limit):
    """Возвращает страницу донатов (включая возвращённые) для админки."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM donations ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return rows


async def get_all_donations():
    """Возвращает все донаты по возрастанию id для экспорта."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM donations ORDER BY id ASC")
        rows = await cursor.fetchall()
        return rows


async def find_donations(query):
    """Ищет донаты по user_id или части username."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        clean_query = query.lstrip("@")
        if clean_query.isdigit():
            cursor = await db.execute(
                "SELECT * FROM donations WHERE user_id = ? "
                "ORDER BY id DESC LIMIT 20",
                (int(clean_query),),
            )
        else:
            like_value = "%" + clean_query + "%"
            cursor = await db.execute(
                "SELECT * FROM donations WHERE username LIKE ? "
                "ORDER BY id DESC LIMIT 20",
                (like_value,),
            )
        rows = await cursor.fetchall()
        return rows


async def is_user_blocked(user_id):
    """Проверяет, заблокирован ли пользователь для функции обратной связи."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        if row[0] == 1:
            return True
        return False


async def set_user_blocked(user_id, is_blocked):
    """Устанавливает флаг блокировки пользователя (1 или 0)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_blocked = ? WHERE user_id = ?",
            (is_blocked, user_id),
        )
        await db.commit()


async def add_contact_message(user_id, direction, content_type, from_chat_id,
                              message_id):
    """Логирует одно сообщение в переписке пользователь-админ."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO contact_messages "
            "(user_id, direction, content_type, from_chat_id, message_id, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, direction, content_type, from_chat_id, message_id, now),
        )
        await db.commit()
        return cursor.lastrowid


async def get_last_contact_message_time(user_id, direction):
    """Возвращает created_at последнего сообщения пользователя в заданном направлении или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT created_at FROM contact_messages "
            "WHERE user_id = ? AND direction = ? ORDER BY id DESC LIMIT 1",
            (user_id, direction),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def get_setting(key):
    """Возвращает значение настройки или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def set_setting(key, value):
    """Сохраняет значение настройки."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Бэкап / восстановление
# ---------------------------------------------------------------------------


async def backup_to(dest_path):
    """Пишет консистентный снимок живой БД в dest_path через online backup API.

    Снимок атомарный даже во время работы бота — в отличие от сырого
    копирования файла, которое может дать «рваную» копию. dest_path не должен
    существовать заранее.
    """
    async with aiosqlite.connect(DB_PATH) as src:
        dest = await aiosqlite.connect(dest_path)
        try:
            await src.backup(dest)
        finally:
            await dest.close()


async def restore_from(src_path):
    """Заменяет содержимое живой БД содержимым src_path через online backup API.

    Проверяет, что src — валидная база этого бота (есть таблица users).
    Бросает ValueError, если файл не похож на базу.
    """
    async with aiosqlite.connect(src_path) as src:
        async with src.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='users'"
        ) as cursor:
            if await cursor.fetchone() is None:
                raise ValueError(
                    "Файл не похож на базу этого бота (нет таблицы users)."
                )
        async with aiosqlite.connect(DB_PATH) as live:
            await src.backup(live)
            await live.commit()
