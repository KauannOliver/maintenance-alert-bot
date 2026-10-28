import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    _allowed_users_raw = os.getenv("TELEGRAM_ALLOWED_USERS", "")
    TELEGRAM_ALLOWED_USERS = [u.strip() for u in _allowed_users_raw.split(",") if u.strip()]
    
    _alert_chats_raw = os.getenv("TELEGRAM_ALERT_CHAT_IDS", "")
    TELEGRAM_ALERT_CHAT_IDS = [c.strip() for c in _alert_chats_raw.split(",") if c.strip()]

    # MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "om_digital")
    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "report#EN2025")

    # Application
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 60))
    COLD_START_DAYS = int(os.getenv("COLD_START_DAYS", 2))
    STEADY_STATE_BUFFER_MINUTES = int(os.getenv("STEADY_STATE_BUFFER_MINUTES", 5))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # SQLite
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "omsentinel.db")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_ALLOWED_USERS:
            missing.append("TELEGRAM_ALLOWED_USERS")
        if not cls.TELEGRAM_ALERT_CHAT_IDS:
            missing.append("TELEGRAM_ALERT_CHAT_IDS")
            
        if missing:
            raise ValueError(f"Missing required configuration variables: {', '.join(missing)}")
