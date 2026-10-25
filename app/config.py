import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

APP_LOGIN = os.getenv("APP_LOGIN", "admin")
APP_PASSWORD = os.getenv("APP_PASSWORD", "change-me")
APP_TITLE = os.getenv("APP_TITLE", "Камчатский медиамониторинг")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID", "")
SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "5"))
