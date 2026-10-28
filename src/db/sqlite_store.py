import sqlite3
import json
from datetime import datetime
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class SQLiteStore:
    def __init__(self):
        self.db_path = Config.SQLITE_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # sent_alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fingerprint TEXT NOT NULL UNIQUE,
                    cod_om TEXT NOT NULL,
                    rules_json TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    payload_json TEXT
                )
            ''')
            
            # poll_state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS poll_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_successful_poll_at TEXT,
                    last_window_start TEXT,
                    last_cycle_status TEXT,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Seed poll_state if empty
            cursor.execute('SELECT COUNT(*) FROM poll_state')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO poll_state (id, updated_at) 
                    VALUES (1, ?)
                ''', (datetime.now().isoformat(),))

            # bot_control table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_control (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    is_paused INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Seed bot_control if empty
            cursor.execute('SELECT COUNT(*) FROM bot_control')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO bot_control (id, is_paused, updated_at) 
                    VALUES (1, 0, ?)
                ''', (datetime.now().isoformat(),))
            
            conn.commit()

    def is_paused(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT is_paused FROM bot_control WHERE id = 1')
            row = cursor.fetchone()
            return bool(row[0]) if row else False

    def set_paused(self, paused: bool):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bot_control 
                SET is_paused = ?, updated_at = ? 
                WHERE id = 1
            ''', (1 if paused else 0, datetime.now().isoformat()))
            conn.commit()

    def get_last_successful_poll_at(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT last_successful_poll_at FROM poll_state WHERE id = 1')
            row = cursor.fetchone()
            return row[0] if row else None

    def set_poll_success(self, window_start: str, poll_at: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE poll_state 
                SET last_successful_poll_at = ?, 
                    last_window_start = ?, 
                    last_cycle_status = 'success', 
                    updated_at = ? 
                WHERE id = 1
            ''', (poll_at, window_start, datetime.now().isoformat()))
            conn.commit()

    def set_poll_failure(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE poll_state 
                SET last_cycle_status = 'failure', 
                    updated_at = ? 
                WHERE id = 1
            ''', (datetime.now().isoformat(),))
            conn.commit()

    def was_alert_sent(self, fingerprint: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM sent_alerts WHERE fingerprint = ?', (fingerprint,))
            return cursor.fetchone() is not None

    def save_sent_alert(self, fingerprint, cod_om, rules_list, chat_id, payload_dict):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sent_alerts (fingerprint, cod_om, rules_json, chat_id, sent_at, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                fingerprint, 
                cod_om, 
                json.dumps(rules_list), 
                str(chat_id), 
                datetime.now().isoformat(),
                json.dumps(payload_dict)
            ))
            conn.commit()

    def get_recent_alerts(self, limit=10):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cod_om, rules_json, sent_at 
                FROM sent_alerts 
                ORDER BY sent_at DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()

    def count_sent_alerts(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM sent_alerts')
            return cursor.fetchone()[0]
