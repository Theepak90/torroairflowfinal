import pymysql
import logging
from flask import current_app
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def get_db_config():
    return {
        'host': current_app.config['MYSQL_HOST'],
        'port': current_app.config['MYSQL_PORT'],
        'user': current_app.config['MYSQL_USER'],
        'password': current_app.config['MYSQL_PASSWORD'],
        'database': current_app.config['MYSQL_DATABASE'],
        'cursorclass': pymysql.cursors.DictCursor,
        'charset': 'utf8mb4'
    }


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = pymysql.connect(**get_db_config())
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
