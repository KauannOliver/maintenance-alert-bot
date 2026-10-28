from src.db.sqlite_store import SQLiteStore
import logging

logger = logging.getLogger(__name__)

class Deduplicator:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def is_new_finding(self, finding):
        """
        Determines whether the finding has already been processed and sent.
        """
        fingerprint = finding.get("fingerprint")
        if not fingerprint:
            return False
            
        return not self.store.was_alert_sent(fingerprint)

    def mark_as_sent(self, finding, chat_id):
        """
        Persists the finding fingerprint to deduplication storage.
        """
        try:
            self.store.save_sent_alert(
                fingerprint=finding["fingerprint"],
                cod_om=finding["cod_om"],
                rules_list=finding["rules_triggered"],
                chat_id=chat_id,
                payload_dict=finding
            )
            return True
        except Exception as e:
            logger.error(f"Error persisting sent alert: {e}")
            return False
