import mysql.connector
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class MySQLClient:
    def __init__(self):
        self.config = {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'connect_timeout': 10
        }

    def fetch_all(self, query, params=None):
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing MySQL query: {e}")
            raise
        finally:
            if conn:
                conn.close()
