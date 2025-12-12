import pymysql
import logging
from flask import current_app
from contextlib import contextmanager
from dbutils.pooled_db import PooledDB

logger = logging.getLogger(__name__)

# Global connection pool (initialized in main.py)
_db_pool = None


def init_db_pool(app):
    """Initialize the database connection pool"""
    global _db_pool
    if _db_pool is None:
        _db_pool = PooledDB(
            creator=pymysql,
            mincached=app.config['DB_POOL_MIN'],
            maxcached=app.config['DB_POOL_MAX'],
            maxconnections=app.config['DB_POOL_MAX'],
            blocking=True,  # Block if pool is exhausted
            maxusage=None,  # No limit on connection reuse
            setsession=[],  # No session setup commands
            ping=1,  # Ping connection to check if alive (1 = check on every use)
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE'],
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            autocommit=False
        )
        logger.info('FN:init_db_pool DB_POOL_MIN:{} DB_POOL_MAX:{}'.format(app.config['DB_POOL_MIN'], app.config['DB_POOL_MAX']))


def get_db_pool():
    """Get the database connection pool"""
    if _db_pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _db_pool


@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    pool = get_db_pool()
    conn = None
    try:
        conn = pool.connection()
        yield conn
    except Exception as e:
        logger.error('FN:get_db_connection error:{}'.format(str(e)))
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()  # Return connection to pool
