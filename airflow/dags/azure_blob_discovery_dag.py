from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import json
import pymysql
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.azure_config import (
    AZURE_STORAGE_ACCOUNTS,
    DB_CONFIG,
    get_storage_location_json,
)
from utils.azure_blob_client import AzureBlobClient
from utils.metadata_extractor import extract_file_metadata, generate_file_hash, generate_schema_hash
from utils.deduplication import check_file_exists, should_update_or_insert
from utils.email_notifier import notify_new_discoveries

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


def discover_azure_blobs(**context):
    dag_run = context['dag_run']
    run_id = dag_run.run_id
    discovery_batch_id = f"batch-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    batch_start_time = datetime.utcnow()
    
    logger.info(f"Starting Azure Blob discovery - Batch ID: {discovery_batch_id}, Run ID: {run_id}")
    
    all_new_discoveries = []
    
    for storage_config in AZURE_STORAGE_ACCOUNTS:
        account_name = storage_config["name"]
        connection_string = storage_config["connection_string"]
        containers = storage_config["containers"]
        folders = storage_config.get("folders", [""])
        if not folders or folders == [""]:
            folders = [""]  # Scan root if no folders specified
        environment = storage_config.get("environment", "prod")
        env_type = storage_config.get("env_type", "production")
        data_source_type = storage_config.get("data_source_type", "unknown")
        file_extensions = storage_config.get("file_extensions")  # None = all files
        
        logger.info(f"Processing storage account: {account_name}")
        
        try:
            blob_client = AzureBlobClient(connection_string)
            
            for container_name in containers:
                logger.info(f"Scanning container: {container_name}")
                
                for folder_path in folders:
                    logger.info(f"Scanning folder: {folder_path}")
                    
                    try:
                        blobs = blob_client.list_blobs(
                            container_name=container_name,
                            folder_path=folder_path,
                            file_extensions=file_extensions
                        )
                        
                        logger.info(f"Found {len(blobs)} blobs in {container_name}/{folder_path}")
                        
                        for blob_info in blobs:
                            try:
                                blob_path = blob_info["full_path"]
                                
                                existing_record = check_file_exists(
                                    storage_type="azure_blob",
                                    storage_identifier=account_name,
                                    storage_path=blob_path
                                )
                                
                                # Use ETag for all files - no need to download for hash
                                file_size = blob_info.get("size", 0)
                                etag = blob_info.get("etag", "").strip('"')
                                last_modified = blob_info.get("last_modified")
                                
                                # Create composite hash from ETag + size + last_modified (no download needed)
                                composite_string = f"{etag}_{file_size}_{last_modified.isoformat() if last_modified else ''}"
                                file_hash = generate_file_hash(composite_string.encode('utf-8'))
                                
                                # Get ONLY headers/column names - NO data rows (banking compliance)
                                # CSV/JSON: First 1KB (just headers/keys - NO data)
                                # Parquet: Last 8KB (schema metadata is at the end - column names only)
                                file_sample = None
                                file_extension = blob_info["name"].split(".")[-1].lower() if "." in blob_info["name"] else ""
                                
                                try:
                                    if file_extension == "parquet":
                                        # Parquet metadata is at the end - get tail (column names only)
                                        file_sample = blob_client.get_blob_tail(container_name, blob_path, max_bytes=8192)
                                        logger.info(f"Got tail sample for parquet schema (column names only): {blob_path} ({len(file_sample)} bytes)")
                                    else:
                                        # CSV/JSON: Just need headers/keys from the beginning - NO data rows
                                        file_sample = blob_client.get_blob_sample(container_name, blob_path, max_bytes=1024)
                                        logger.info(f"Got header sample (column names only, NO data): {blob_path} ({len(file_sample)} bytes)")
                                except Exception as e:
                                    logger.warning(f"Could not get blob sample for {blob_path}: {str(e)}")
                                
                                # Use ETag-based hash for all files (no full download)
                                # Extract schema from sample if available
                                if file_sample:
                                    metadata = extract_file_metadata(blob_info, file_sample)
                                    schema_hash = metadata.get("schema_hash", generate_schema_hash({}))
                                else:
                                    # No sample available, create minimal metadata
                                    schema_hash = generate_schema_hash({})
                                    metadata = {
                                        "file_metadata": {
                                            "basic": {
                                                "name": blob_info["name"],
                                                "extension": "." + blob_info["name"].split(".")[-1] if "." in blob_info["name"] else "",
                                                "format": blob_info["name"].split(".")[-1].lower() if "." in blob_info["name"] else "unknown",
                                                "size_bytes": file_size,
                                                "content_type": blob_info.get("content_type", "application/octet-stream"),
                                                "mime_type": blob_info.get("content_type", "application/octet-stream")
                                            },
                                            "hash": {
                                                "algorithm": "sha256_etag_composite",
                                                "value": file_hash,
                                                "computed_at": datetime.utcnow().isoformat() + "Z",
                                                "source": "etag_composite"
                                            },
                                            "timestamps": {
                                                "created_at": blob_info["created_at"].isoformat() if blob_info.get("created_at") else None,
                                                "last_modified": blob_info["last_modified"].isoformat() if blob_info.get("last_modified") else None
                                            }
                                        },
                                        "schema_json": {},
                                        "schema_hash": schema_hash,
                                        "file_hash": file_hash,
                                        "storage_metadata": {
                                            "azure": {
                                                "type": blob_info.get("blob_type", "Block blob"),
                                                "etag": etag,
                                                "access_tier": blob_info.get("access_tier"),
                                                "creation_time": blob_info["created_at"].isoformat() if blob_info.get("created_at") else None,
                                                "last_modified": blob_info["last_modified"].isoformat() if blob_info.get("last_modified") else None,
                                                "lease_status": blob_info.get("lease_status"),
                                                "content_encoding": blob_info.get("content_encoding"),
                                                "content_language": blob_info.get("content_language"),
                                                "cache_control": blob_info.get("cache_control"),
                                                "metadata": blob_info.get("metadata", {})
                                            }
                                        }
                                    }
                                
                                # Ensure file_hash is set
                                if "file_hash" not in metadata:
                                    metadata["file_hash"] = file_hash
                                
                                file_metadata = metadata.get("file_metadata")
                                
                                if not should_update_or_insert(existing_record, file_hash, schema_hash):
                                    logger.info(f"Skipping {blob_path} - already exists with same content")
                                    continue
                                
                                storage_location = get_storage_location_json(
                                    account_name=account_name,
                                    container=container_name,
                                    blob_path=blob_path
                                )
                                
                                discovery_info = {
                                    "batch": {
                                        "id": discovery_batch_id,
                                        "started_at": batch_start_time.isoformat() + "Z"
                                    },
                                    "source": {
                                        "type": "airflow_dag",
                                        "name": "azure_blob_discovery_dag",
                                        "run_id": run_id
                                    },
                                    "scan": {
                                        "container": container_name,
                                        "folder": folder_path
                                    }
                                }
                                
                                conn = get_db_connection()
                                try:
                                    with conn.cursor() as cursor:
                                        if existing_record:
                                            update_sql = """
                                                UPDATE data_discovery
                                                SET file_metadata = %s,
                                                    schema_json = %s,
                                                    schema_hash = %s,
                                                    storage_metadata = %s,
                                                    discovery_info = %s,
                                                    last_checked_at = NOW(),
                                                    updated_at = NOW()
                                                WHERE id = %s
                                            """
                                            cursor.execute(update_sql, (
                                                json.dumps(file_metadata),
                                                json.dumps(metadata.get("schema_json", {})),
                                                schema_hash,
                                                json.dumps(metadata.get("storage_metadata", {})),
                                                json.dumps(discovery_info),
                                                existing_record["id"]
                                            ))
                                            discovery_id = existing_record["id"]
                                            logger.info(f"Updated discovery ID {discovery_id} for {blob_path}")
                                        else:
                                            insert_sql = """
                                                INSERT INTO data_discovery (
                                                    storage_location, file_metadata, schema_json, schema_hash,
                                                    discovered_at, status, approval_status, is_visible, is_active,
                                                    environment, env_type, data_source_type, folder_path,
                                                    storage_metadata, storage_data_metadata, discovery_info,
                                                    created_by
                                                ) VALUES (
                                                    %s, %s, %s, %s,
                                                    NOW(), 'pending', 'pending_review', TRUE, TRUE,
                                                    %s, %s, %s, %s, %s, %s, %s, 'airflow'
                                                )
                                            """
                                            
                                            cursor.execute(insert_sql, (
                                                json.dumps(storage_location),
                                                json.dumps(file_metadata),
                                                json.dumps(metadata.get("schema_json", {})),
                                                schema_hash,
                                                environment,
                                                env_type,
                                                data_source_type,
                                                folder_path,
                                                json.dumps(metadata.get("storage_metadata", {})),
                                                json.dumps({}),
                                                json.dumps(discovery_info),
                                            ))
                                            
                                            discovery_id = cursor.lastrowid
                                            logger.info(f"✅ Inserted discovery ID {discovery_id} for {blob_path}")
                                        
                                        conn.commit()
                                        
                                        all_new_discoveries.append({
                                            "id": discovery_id,
                                            "file_name": file_metadata["basic"]["name"],
                                            "storage_path": blob_path,
                                        })
                                        
                                except Exception as e:
                                    conn.rollback()
                                    logger.error(f"Error inserting discovery for {blob_path}: {str(e)}")
                                    raise
                                finally:
                                    conn.close()
                                    
                            except Exception as e:
                                logger.error(f"Error processing blob {blob_info.get('name', 'unknown')}: {str(e)}")
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error scanning folder {folder_path}: {str(e)}")
                        continue
            
        except Exception as e:
            logger.error(f"Error processing storage account {account_name}: {str(e)}")
            continue
    
    batch_end_time = datetime.utcnow()
    duration_ms = int((batch_end_time - batch_start_time).total_seconds() * 1000)
    
    logger.info(f"Discovery complete - Found {len(all_new_discoveries)} new discoveries in {duration_ms}ms")
    return len(all_new_discoveries)


default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'azure_blob_discovery',
    default_args=default_args,
    description='Discover new files in Azure Blob Storage every minute',
    schedule_interval='*/1 * * * *',  # Every minute
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=10,  # Allow up to 10 DAG runs to be active
    max_active_tasks=20,  # Allow up to 20 tasks to run simultaneously
    tags=['data-discovery', 'azure-blob'],
)

discovery_task = PythonOperator(
    task_id='discover_azure_blobs',
    python_callable=discover_azure_blobs,
    dag=dag,
)

notification_task = PythonOperator(
    task_id='notify_data_governors',
    python_callable=notify_new_discoveries,
    dag=dag,
)

discovery_task >> notification_task
