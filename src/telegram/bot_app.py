from telegram.ext import ApplicationBuilder
from src.config import Config
from src.db.mysql_client import MySQLClient
from src.db.sqlite_store import SQLiteStore
from src.services.deduplicator import Deduplicator
from src.services.poller import PollerService
from src.telegram.handlers import register_handlers
import logging

logger = logging.getLogger(__name__)

class BotApp:
    def __init__(self):
        # Initialize dependencies
        self.mysql = MySQLClient()
        self.sqlite = SQLiteStore()
        self.deduplicator = Deduplicator(self.sqlite)
        self.poller = PollerService(self.mysql, self.sqlite, self.deduplicator)
        
        # Build Telegram Application
        self.application = ApplicationBuilder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Register Command & Message Handlers
        register_handlers(self.application, self.sqlite)
        
        # Schedule Polling Job
        self.application.job_queue.run_repeating(
            self.poller.run_cycle,
            interval=Config.POLL_INTERVAL_SECONDS,
            first=10 # wait 10s on first run to give bot time to start
        )

    def run(self):
        """Starts the bot."""
        logger.info("🎉 Starting OMSentinel bot...")
        self.application.run_polling()
