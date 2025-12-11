import pymysql
import logging
from typing import Dict, Optional, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.azure_config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_db_connection():
    return pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )


def check_file_exists(
    storage_type: str,
    storage_identifier: str,
    storage_path: str
) -> Optional[Dict]:
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                SELECT id, file_hash, schema_hash
                FROM data_discovery
                WHERE storage_type = %s
                  AND storage_identifier = %s
                  AND storage_path = %s
                LIMIT 1
            """
            cursor.execute(sql, (storage_type, storage_identifier, storage_path))
            result = cursor.fetchone()
            return result
    except Exception as e:
        logger.error(f"Error checking file existence: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()


def compare_hashes(existing_record: Dict, new_file_hash: str, new_schema_hash: str) -> Tuple[bool, bool]:
    existing_file_hash = existing_record.get("file_hash")
    existing_schema_hash = existing_record.get("schema_hash")
    
    file_changed = existing_file_hash != new_file_hash
    schema_changed = existing_schema_hash != new_schema_hash
    
    return file_changed, schema_changed


def should_update_or_insert(existing_record: Optional[Dict], new_file_hash: str, new_schema_hash: str) -> bool:
    if not existing_record:
        return True
    
    file_changed, schema_changed = compare_hashes(existing_record, new_file_hash, new_schema_hash)
    
    if file_changed or schema_changed:
        logger.info(f"File changed detected - file_changed: {file_changed}, schema_changed: {schema_changed}")
        return True
    
    logger.info("File already exists with same content and schema, skipping")
    return False
