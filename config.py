import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
THANK_YOU_STICKER_ID = os.getenv("THANK_YOU_STICKER_ID", "")

DB_PATH = os.getenv("DB_PATH", "bot.db")

MIN_DONATE_AMOUNT = 1
MAX_DONATE_AMOUNT = 10000

REFUND_WINDOW_SECONDS = 24 * 60 * 60
