from datetime import datetime, timedelta
from src.config import Config
from src.db.mysql_client import MySQLClient
from src.db.sqlite_store import SQLiteStore
from src.queries.problematic_oms import GET_PROBLEMATIC_OMS_QUERY
from src.services.rule_engine import RuleEngine
from src.services.deduplicator import Deduplicator
from src.services.formatter import Formatter
import logging
import asyncio

logger = logging.getLogger(__name__)

class PollerService:
    def __init__(self, mysql: MySQLClient, sqlite: SQLiteStore, deduplicator: Deduplicator):
        self.mysql = mysql
        self.sqlite = sqlite
        self.deduplicator = deduplicator

    async def run_cycle(self, context=None):
        """
        Executes a polling cycle: 
        1. Query recent OMs
        2. Detect anomalies
        3. Notify and deduplicate
        """
        if self.sqlite.is_paused():
            logger.info("Polling skipped: Bot is paused.")
            return

        try:
            # 0. Log system time for verification
            now_local = datetime.now()
            logger.info(f"--- Início do Ciclo de Polling | Local Time: {now_local.strftime('%Y-%m-%d %H:%M:%S')} ---")

            # 1. Determine window
            last_poll_str = self.sqlite.get_last_successful_poll_at()
            if not last_poll_str:
                # Cold start
                window_start_dt = datetime.now() - timedelta(days=Config.COLD_START_DAYS)
                logger.info(f"Cold start: fetching since {window_start_dt}")
            else:
                # Steady state with overlap buffer
                last_poll_dt = datetime.fromisoformat(last_poll_str)
                window_start_dt = last_poll_dt - timedelta(minutes=Config.STEADY_STATE_BUFFER_MINUTES)
                logger.info(f"Steady state: fetching since {window_start_dt}")

            # 2. Fetch from MySQL
            # window_start_dt formatted for MySQL
            mysql_param = window_start_dt.strftime('%Y-%m-%d %H:%M:%S')
            rows = self.mysql.fetch_all(GET_PROBLEMATIC_OMS_QUERY, (mysql_param,))
            logger.info(f"Retrieved {len(rows)} candidate rows from MySQL.")

            # 3. Process each row
            new_alerts_count = 0
            for row in rows:
                finding = RuleEngine.classify_row(row)
                if finding and self.deduplicator.is_new_finding(finding):
                    # 4. Format and Send
                    msg = Formatter.format_alert(finding)
                    success = await self._send_to_all_chats(msg, context)
                    
                    if success:
                        # 5. Persist fingerprint only on success
                        self.deduplicator.mark_as_sent(finding, "broadcasting") # we track by fingerprint mostly
                        new_alerts_count += 1
            
            # 6. Update state
            self.sqlite.set_poll_success(
                window_start=window_start_dt.isoformat(),
                poll_at=datetime.now().isoformat()
            )
            logger.info(f"Cycle completed. Sent {new_alerts_count} new alerts.")

        except Exception as e:
            logger.error(f"Error in poller cycle: {e}")
            self.sqlite.set_poll_failure()
            # In a job queue, we let the exception propagate or handle it to avoid crashing the whole bot
            raise e

    async def _send_to_all_chats(self, msg, context):
        """Sends a message to all configured alert chat IDs."""
        if not context or not hasattr(context, 'bot'):
            logger.error("No bot context available to send messages.")
            return False

        all_success = True
        for chat_id in Config.TELEGRAM_ALERT_CHAT_IDS:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Failed to send alert to chat {chat_id}: {e}")
                all_success = False
        
        return all_success
