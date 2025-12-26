from flask import Blueprint, request, jsonify
from app.services.discovery_service import DiscoveryService
import logging
import json
import os
import sys
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

discovery_bp = Blueprint('discovery', __name__, url_prefix='/api/discovery')


@discovery_bp.route('', methods=['GET'])
def get_discoveries():
    try:
        # Validate and parse page parameter
        try:
            page = int(request.args.get('page', 0))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid page parameter. Must be a non-negative integer.'}), 400
        
        # Validate page is non-negative
        if page < 0:
            return jsonify({'error': 'Page parameter must be a non-negative integer.'}), 400
        
        # Validate and parse size parameter
        try:
            size = int(request.args.get('size', 50))
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid size parameter. Must be a positive integer.'}), 400
        
        # Enforce strict size limits
        if size > 100:
            size = 100
        if size < 1:
            size = 50
        
        status = request.args.get('status')
        environment = request.args.get('environment')
        data_source_type = request.args.get('data_source_type')
        search = request.args.get('search')
        
        discoveries, pagination = DiscoveryService.get_discoveries(
            page=page,
            size=size,
            status=status,
            environment=environment,
            data_source_type=data_source_type,
            search=search
        )
        
        return jsonify({
            'discoveries': discoveries,
            'pagination': pagination
        }), 200
        
    except Exception as e:
        page_val = page if 'page' in locals() else 'N/A'
        size_val = size if 'size' in locals() else 'N/A'
        logger.error(f'FN:get_discoveries page:{page_val} size:{size_val} error:{str(e)}')
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>', methods=['GET'])
def get_discovery(discovery_id):
    try:
        discovery = DiscoveryService.get_discovery_by_id(discovery_id)
        
        if not discovery:
            return jsonify({'error': 'Discovery not found'}), 404
        
        return jsonify(discovery), 200
        
    except Exception as e:
        logger.error(f'FN:get_discovery discovery_id:{discovery_id} error:{str(e)}')
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>/approve', methods=['PUT'])
def approve_discovery(discovery_id):
    try:
        # Validate JSON payload exists
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        approved_by = data.get('approved_by')
        role = data.get('role')
        comments = data.get('comments')
        
        # Validate required field
        if not approved_by or not isinstance(approved_by, str) or not approved_by.strip():
            return jsonify({'error': 'approved_by is required and must be a non-empty string'}), 400
        
        discovery = DiscoveryService.approve_discovery(discovery_id, approved_by, role, comments)
        
        return jsonify({
            'message': 'Discovery approved successfully',
            'discovery': discovery
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        approved_by_val = data.get('approved_by', 'N/A') if 'data' in locals() else 'N/A'
        logger.error(f'FN:approve_discovery discovery_id:{discovery_id} approved_by:{approved_by_val} error:{str(e)}')
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/<int:discovery_id>/reject', methods=['PUT'])
def reject_discovery(discovery_id):
    try:
        # Validate JSON payload exists
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        rejected_by = data.get('rejected_by')
        rejection_reason = data.get('rejection_reason')
        role = data.get('role')
        comments = data.get('comments')
        
        # Validate required field
        if not rejected_by or not isinstance(rejected_by, str) or not rejected_by.strip():
            return jsonify({'error': 'rejected_by is required and must be a non-empty string'}), 400
        
        discovery = DiscoveryService.reject_discovery(discovery_id, rejected_by, rejection_reason, role, comments)
        
        return jsonify({
            'message': 'Discovery rejected successfully',
            'discovery': discovery
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        rejected_by_val = data.get('rejected_by', 'N/A') if 'data' in locals() else 'N/A'
        logger.error(f'FN:reject_discovery discovery_id:{discovery_id} rejected_by:{rejected_by_val} error:{str(e)}')
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        stats = DiscoveryService.get_summary_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f'FN:get_stats error:{str(e)}')
        return jsonify({'error': str(e)}), 500


@discovery_bp.route('/trigger', methods=['POST'])
def trigger_discovery():
    """
    Trigger manual discovery scan - runs the standalone discovery logic
    This scans Azure Blob Storage and discovers new/updated files
    """
    try:
        # Get the project root directory (parent of backend)
        # File is at: backend/app/api/routes/discovery.py
        # Need to go: routes -> api -> app -> backend -> project_root
        current_file = os.path.abspath(__file__)
        backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        project_root = os.path.dirname(backend_path)
        cwd = os.getcwd()
        
        # Try multiple possible locations for airflow directory
        possible_airflow_paths = []
        
        # Check environment variable first (highest priority)
        if os.getenv('AIRFLOW_PATH'):
            possible_airflow_paths.append(os.getenv('AIRFLOW_PATH'))
        
        # Common system paths
        possible_airflow_paths.extend([
            '/opt/airflow',  # Standard Airflow path
            '/app/airflow',  # Common application path
            '/airflow',  # Direct root airflow
        ])
        
        # Project structure paths
        possible_airflow_paths.extend([
            os.path.join(project_root, 'airflow'),  # Standard: project_root/airflow
            os.path.join(backend_path, '..', 'airflow'),  # Alternative: backend/../airflow
            os.path.join(os.path.dirname(backend_path), 'airflow'),  # If backend is nested differently
            os.path.join(cwd, 'airflow'),  # Relative to current working directory
            os.path.join(cwd, '..', 'airflow'),  # Parent of CWD
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for path in possible_airflow_paths:
            abs_path = os.path.abspath(path)
            if abs_path not in seen:
                seen.add(abs_path)
                unique_paths.append(abs_path)
        
        airflow_path = None
        for path in unique_paths:
            if os.path.exists(path) and os.path.isdir(path):
                airflow_path = path
                logger.info(f'FN:trigger_discovery airflow_path_found: {airflow_path}')
                break
        
        # Validate paths exist
        if not airflow_path:
            tried_paths = ", ".join(unique_paths[:5])  # Show first 5 paths tried
            error_msg = f'Airflow directory not found. Tried: {tried_paths}. Current file: {current_file[:100]}, Backend path: {backend_path[:100]}, Project root: {project_root[:100]}, CWD: {cwd[:100]}. Set AIRFLOW_PATH environment variable to specify custom location.'
            logger.error(f'FN:trigger_discovery path_error: {error_msg}')
            return jsonify({'error': error_msg}), 500
        
        # Add airflow to path (must be first for imports to work)
        if airflow_path not in sys.path:
            sys.path.insert(0, airflow_path)
        
        # Import discovery function
        try:
            from dotenv import load_dotenv
        except ImportError as e:
            error_msg = f'Failed to import dotenv: {str(e)}. Install with: pip install python-dotenv'
            logger.error(f'FN:trigger_discovery import_error: {error_msg}')
            return jsonify({'error': error_msg}), 500
        
        # Load .env from airflow directory
        airflow_env = os.path.join(airflow_path, '.env')
        if not os.path.exists(airflow_env):
            logger.warning(f'FN:trigger_discovery env_file_not_found: {airflow_env}')
        load_dotenv(airflow_env, override=True)
        
        # Dynamic imports from airflow directory (added to sys.path above)
        # These imports are resolved at runtime after adding airflow_path to sys.path
        try:
            from config.azure_config import AZURE_STORAGE_ACCOUNTS, DB_CONFIG, get_storage_location_json  # type: ignore
            from utils.azure_blob_client import AzureBlobClient  # type: ignore
            from utils.azure_datalake_client import AzureDataLakeClient  # type: ignore
            from utils.path_parser import parse_storage_path  # type: ignore
            from utils.metadata_extractor import extract_file_metadata, generate_file_hash, generate_schema_hash  # type: ignore
            from utils.deduplication import check_file_exists, should_update_or_insert  # type: ignore
            import pymysql
        except ImportError as e:
            error_msg = f'Failed to import airflow modules: {str(e)}. Check if airflow directory exists and dependencies are installed.'
            logger.error(f'FN:trigger_discovery import_error: {error_msg}')
            logger.error(f'FN:trigger_discovery airflow_path: {airflow_path}, sys.path: {sys.path[:3]}')
            return jsonify({'error': error_msg}), 500
        
        def run_discovery():
            """Run discovery in background thread"""
            try:
                # Ensure airflow path is in sys.path for this thread
                if airflow_path not in sys.path:
                    sys.path.insert(0, airflow_path)
                
                # Re-import after ensuring path is set (for thread safety)
                from config.azure_config import AZURE_STORAGE_ACCOUNTS, DB_CONFIG, get_storage_location_json  # type: ignore
                from utils.azure_blob_client import AzureBlobClient  # type: ignore
                from utils.azure_datalake_client import AzureDataLakeClient  # type: ignore
                from utils.path_parser import parse_storage_path  # type: ignore
                from utils.metadata_extractor import extract_file_metadata, generate_file_hash, generate_schema_hash  # type: ignore
                from utils.deduplication import check_file_exists, should_update_or_insert  # type: ignore
                
                batch_start_time = datetime.utcnow()
                discovery_batch_id = f"batch_{int(batch_start_time.timestamp())}"
                run_id = f"manual_{int(batch_start_time.timestamp())}"
                all_new_discoveries = []
                
                for storage_config in AZURE_STORAGE_ACCOUNTS:
                    account_name = storage_config["name"]
                    auth_method = storage_config.get("auth_method", "connection_string")
                    connection_string = storage_config.get("connection_string", "")
                    storage_type = storage_config.get("storage_type", "blob")  # "blob" or "datalake"
                    containers = storage_config["containers"]
                    folders = storage_config.get("folders", [""])
                    if not folders or folders == [""]:
                        folders = [""]
                    datalake_paths = storage_config.get("datalake_paths", [])  # ABFS paths for Data Lake
                    environment = storage_config.get("environment", "prod")
                    env_type = storage_config.get("env_type", "production")
                    data_source_type = storage_config.get("data_source_type", "unknown")
                    file_extensions = storage_config.get("file_extensions")
                    
                    try:
                        # Handle Data Lake Storage Gen2
                        if storage_type == "datalake" or (datalake_paths and len(datalake_paths) > 0):
                            logger.info('FN:trigger_discovery processing_datalake_storage')
                            
                            # Initialize Data Lake client (requires service principal)
                            if not (storage_config.get("client_id") and storage_config.get("client_secret") and storage_config.get("tenant_id")):
                                logger.error('FN:trigger_discovery datalake_requires_service_principal')
                                continue
                            
                            datalake_client = AzureDataLakeClient(
                                account_name=account_name,
                                client_id=storage_config.get("client_id", ""),
                                client_secret=storage_config.get("client_secret", ""),
                                tenant_id=storage_config.get("tenant_id", "")
                            )
                            
                            # Process Data Lake paths if provided (supports ABFS and future formats)
                            if datalake_paths and len(datalake_paths) > 0:
                                for storage_path in datalake_paths:
                                    try:
                                        # Use flexible path parser (supports ABFS and extensible for future formats)
                                        parsed = parse_storage_path(storage_path)
                                        
                                        # Validate it's a Data Lake path
                                        if parsed["storage_type"] != "azure_datalake":
                                            logger.warning(f'FN:trigger_discovery path:{storage_path} storage_type:{parsed["storage_type"]} expected:azure_datalake')
                                            continue
                                        
                                        filesystem_name = parsed["filesystem"]
                                        path = parsed["path"]
                                        # Use account_name from parsed path if available, otherwise use config
                                        if not account_name and parsed.get("account_name"):
                                            account_name = parsed["account_name"]
                                        
                                        logger.info(f'FN:trigger_discovery datalake_filesystem:{filesystem_name} path:{path}')
                                        
                                        # List files in the Data Lake path
                                        files = datalake_client.list_paths(
                                            filesystem_name=filesystem_name,
                                            directory_path=path,
                                            recursive=True
                                        )
                                        
                                        logger.info(f'FN:trigger_discovery datalake_filesystem:{filesystem_name} path:{path} file_count:{len(files)}')
                                        
                                        # Process each file (similar to blob processing)
                                        for file_info in files:
                                            try:
                                                file_path = file_info["full_path"]
                                                
                                                # Check if file exists
                                                conn = pymysql.connect(
                                                    host=DB_CONFIG["host"],
                                                    port=DB_CONFIG["port"],
                                                    user=DB_CONFIG["user"],
                                                    password=DB_CONFIG["password"],
                                                    database=DB_CONFIG["database"],
                                                    cursorclass=pymysql.cursors.DictCursor
                                                )
                                                try:
                                                    with conn.cursor() as cursor:
                                                        cursor.execute("""
                                                            SELECT id, file_hash, schema_hash 
                                                            FROM data_discovery 
                                                            WHERE storage_type = %s 
                                                            AND storage_identifier = %s 
                                                            AND storage_path = %s
                                                            LIMIT 1
                                                        """, ("azure_datalake", account_name, file_path))
                                                        existing_record = cursor.fetchone()
                                                finally:
                                                    conn.close()
                                                
                                                # Generate file hash
                                                file_size = file_info.get("size", 0)
                                                etag = file_info.get("etag", "").strip('"')
                                                last_modified = file_info.get("last_modified")
                                                composite_string = f"{etag}_{file_size}_{last_modified.isoformat() if last_modified else ''}"
                                                file_hash = generate_file_hash(composite_string.encode('utf-8'))
                                                
                                                # Get file sample
                                                file_sample = None
                                                file_extension = file_info["name"].split(".")[-1].lower() if "." in file_info["name"] else ""
                                                
                                                try:
                                                    if file_extension == "parquet":
                                                        file_sample = datalake_client.get_file_sample(filesystem_name, file_path, max_bytes=8192)
                                                    else:
                                                        file_sample = datalake_client.get_file_sample(filesystem_name, file_path, max_bytes=2048)
                                                except Exception:
                                                    pass
                                                
                                                # Extract metadata
                                                if file_sample:
                                                    metadata = extract_file_metadata(file_info, file_sample)
                                                    schema_hash = metadata.get("schema_hash", generate_schema_hash({}))
                                                else:
                                                    schema_hash = generate_schema_hash({})
                                                    metadata = {
                                                        "file_metadata": {
                                                            "basic": {
                                                                "name": file_info["name"],
                                                                "extension": "." + file_info["name"].split(".")[-1] if "." in file_info["name"] else "",
                                                                "format": file_extension,
                                                                "size_bytes": file_size,
                                                                "content_type": file_info.get("content_type", "application/octet-stream"),
                                                                "mime_type": file_info.get("content_type", "application/octet-stream")
                                                            },
                                                            "hash": {
                                                                "algorithm": "shake128_etag_composite",
                                                                "value": file_hash,
                                                                "computed_at": datetime.utcnow().isoformat() + "Z",
                                                                "source": "etag_composite"
                                                            },
                                                            "timestamps": {
                                                                "created_at": file_info.get("created_at").isoformat() if file_info.get("created_at") else None,
                                                                "last_modified": last_modified.isoformat() if last_modified else None
                                                            }
                                                        },
                                                        "schema_json": {},
                                                        "schema_hash": schema_hash,
                                                        "file_hash": file_hash
                                                    }
                                                
                                                if "file_hash" not in metadata:
                                                    metadata["file_hash"] = file_hash
                                                
                                                file_metadata = metadata.get("file_metadata")
                                                
                                                # Check if update needed
                                                should_update, schema_changed = should_update_or_insert(
                                                    existing_record,
                                                    file_hash,
                                                    schema_hash
                                                )
                                                
                                                if should_update or not existing_record:
                                                    storage_location_json = {
                                                        "type": "azure_datalake",
                                                        "path": file_path,
                                                        "connection": {
                                                            "method": "service_principal",
                                                            "account_name": account_name or parsed.get("account_name", "")
                                                        },
                                                        "filesystem": {
                                                            "name": filesystem_name,
                                                            "type": "datalake_filesystem"
                                                        },
                                                        "original_path": parsed.get("original_path", storage_path),
                                                        "metadata": {}
                                                    }
                                                    
                                                    conn = pymysql.connect(
                                                        host=DB_CONFIG["host"],
                                                        port=DB_CONFIG["port"],
                                                        user=DB_CONFIG["user"],
                                                        password=DB_CONFIG["password"],
                                                        database=DB_CONFIG["database"],
                                                        cursorclass=pymysql.cursors.DictCursor
                                                    )
                                                    try:
                                                        with conn.cursor() as cursor:
                                                            if existing_record and existing_record.get("id"):
                                                                # Check if schema changed
                                                                existing_schema_hash = existing_record.get("schema_hash")
                                                                schema_changed = (existing_schema_hash != schema_hash)
                                                                
                                                                if schema_changed:
                                                                    sql = """
                                                                        UPDATE data_discovery
                                                                        SET file_metadata = %s,
                                                                            schema_json = %s,
                                                                            schema_hash = %s,
                                                                            storage_metadata = %s,
                                                                            storage_data_metadata = %s,
                                                                            discovery_info = %s,
                                                                            last_checked_at = NOW(),
                                                                            updated_at = NOW()
                                                                        WHERE id = %s
                                                                    """
                                                                    discovery_info = {
                                                                        "batch": {
                                                                            "id": discovery_batch_id,
                                                                            "started_at": batch_start_time.isoformat() + "Z"
                                                                        },
                                                                        "source": {
                                                                            "type": "manual_trigger",
                                                                            "name": "api_trigger",
                                                                            "run_id": run_id
                                                                        },
                                                                        "scan": {
                                                                            "filesystem": filesystem_name,
                                                                            "path": path
                                                                        }
                                                                    }
                                                                    cursor.execute(sql, (
                                                                        json.dumps(file_metadata),
                                                                        json.dumps(metadata.get("schema_json", {})),
                                                                        schema_hash,
                                                                        json.dumps(metadata.get("storage_metadata", {})),
                                                                        json.dumps(metadata.get("structured_metadata", {})),
                                                                        json.dumps(discovery_info),
                                                                        existing_record["id"]
                                                                    ))
                                                                else:
                                                                    sql = """
                                                                        UPDATE data_discovery
                                                                        SET last_checked_at = NOW()
                                                                        WHERE id = %s
                                                                    """
                                                                    cursor.execute(sql, (existing_record["id"],))
                                                            else:
                                                                sql = """
                                                                    INSERT INTO data_discovery (
                                                                        storage_location, file_metadata, schema_json, schema_hash,
                                                                        discovered_at, status, approval_status, is_visible, is_active,
                                                                        environment, env_type, data_source_type, folder_path,
                                                                        storage_metadata, storage_data_metadata, discovery_info,
                                                                        created_by
                                                                    ) VALUES (
                                                                        %s, %s, %s, %s,
                                                                        NOW(), 'pending', 'pending_review', TRUE, TRUE,
                                                                        %s, %s, %s, %s, %s, %s, %s, 'api_trigger'
                                                                    )
                                                                """
                                                                discovery_info = {
                                                                    "batch": {
                                                                        "id": discovery_batch_id,
                                                                        "started_at": batch_start_time.isoformat() + "Z"
                                                                    },
                                                                    "source": {
                                                                        "type": "manual_trigger",
                                                                        "name": "api_trigger",
                                                                        "run_id": run_id
                                                                    },
                                                                    "scan": {
                                                                        "filesystem": filesystem_name,
                                                                        "path": path
                                                                    }
                                                                }
                                                                cursor.execute(sql, (
                                                                    json.dumps(storage_location_json),
                                                                    json.dumps(file_metadata),
                                                                    json.dumps(metadata.get("schema_json", {})),
                                                                    schema_hash,
                                                                    environment,
                                                                    env_type,
                                                                    data_source_type,
                                                                    path,
                                                                    json.dumps(metadata.get("storage_metadata", {})),
                                                                    json.dumps(metadata.get("structured_metadata", {})),
                                                                    json.dumps(discovery_info),
                                                                ))
                                                                new_id = cursor.lastrowid
                                                                all_new_discoveries.append({
                                                                    "id": new_id,
                                                                    "file_name": file_info["name"],
                                                                    "storage_path": file_path
                                                                })
                                                            conn.commit()
                                                    except Exception as e:
                                                        conn.rollback()
                                                        logger.error(f'FN:trigger_discovery datalake_db_error:{str(e)}')
                                                    finally:
                                                        conn.close()
                                            except Exception as e:
                                                logger.error(f'FN:trigger_discovery datalake_file_error:{str(e)}')
                                                continue
                                    except Exception as e:
                                        logger.error(f'FN:trigger_discovery storage_path:{storage_path} error:{str(e)}')
                                        continue
                            
                            # Continue to next storage config after processing Data Lake
                            continue
                        
                        # Handle Blob Storage (existing logic)
                        # Initialize blob client based on authentication method
                        if auth_method == "service_principal":
                            blob_client = AzureBlobClient(
                                account_name=account_name,
                                client_id=storage_config.get("client_id", ""),
                                client_secret=storage_config.get("client_secret", ""),
                                tenant_id=storage_config.get("tenant_id", "")
                            )
                        else:
                            blob_client = AzureBlobClient(connection_string=connection_string)
                        
                        # If containers list is empty, scan all containers
                        if not containers or len(containers) == 0:
                            logger.info('FN:trigger_discovery containers_empty_scanning_all')
                            containers = blob_client.list_containers()
                            logger.info(f'FN:trigger_discovery found_containers:{len(containers)}')
                        
                        for container_name in containers:
                            for folder_path in folders:
                                try:
                                    blobs = blob_client.list_blobs(
                                        container_name=container_name,
                                        folder_path=folder_path,
                                        file_extensions=file_extensions
                                    )
                                    
                                    for blob_info in blobs:
                                        try:
                                            blob_path = blob_info["full_path"]
                                            
                                            # Check if exists
                                            conn = pymysql.connect(
                                                host=DB_CONFIG["host"],
                                                port=DB_CONFIG["port"],
                                                user=DB_CONFIG["user"],
                                                password=DB_CONFIG["password"],
                                                database=DB_CONFIG["database"],
                                                cursorclass=pymysql.cursors.DictCursor
                                            )
                                            try:
                                                with conn.cursor() as cursor:
                                                    cursor.execute("""
                                                        SELECT id, file_hash, schema_hash 
                                                        FROM data_discovery 
                                                        WHERE storage_type = %s 
                                                        AND storage_identifier = %s 
                                                        AND storage_path = %s
                                                        LIMIT 1
                                                    """, ("azure_blob", account_name, blob_path))
                                                    existing_record = cursor.fetchone()
                                            finally:
                                                conn.close()
                                            
                                            # Generate file hash
                                            file_size = blob_info.get("size", 0)
                                            etag = blob_info.get("etag", "").strip('"')
                                            last_modified = blob_info.get("last_modified")
                                            composite_string = f"{etag}_{file_size}_{last_modified.isoformat() if last_modified else ''}"
                                            file_hash = generate_file_hash(composite_string.encode('utf-8'))
                                            
                                            # Get file sample
                                            file_sample = None
                                            file_extension = blob_info["name"].split(".")[-1].lower() if "." in blob_info["name"] else ""
                                            
                                            try:
                                                if file_extension == "parquet":
                                                    file_sample = blob_client.get_blob_tail(container_name, blob_path, max_bytes=8192)
                                                else:
                                                    # CSV/JSON: Get headers + 1-2 sample rows for reference (banking compliance)
                                                    file_sample = blob_client.get_blob_sample(container_name, blob_path, max_bytes=2048)
                                            except Exception:
                                                pass
                                            
                                            # Extract metadata
                                            if file_sample:
                                                metadata = extract_file_metadata(blob_info, file_sample)
                                                schema_hash = metadata.get("schema_hash", generate_schema_hash({}))
                                            else:
                                                schema_hash = generate_schema_hash({})
                                                metadata = {
                                                    "file_metadata": {
                                                        "basic": {
                                                            "name": blob_info["name"],
                                                            "extension": "." + blob_info["name"].split(".")[-1] if "." in blob_info["name"] else "",
                                                            "format": file_extension,
                                                            "size_bytes": file_size,
                                                            "content_type": blob_info.get("content_type", "application/octet-stream"),
                                                            "mime_type": blob_info.get("content_type", "application/octet-stream")
                                                        },
                                                        "hash": {
                                                            "algorithm": "shake128_etag_composite",
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
                                                    "file_hash": file_hash
                                                }
                                            
                                            if "file_hash" not in metadata:
                                                metadata["file_hash"] = file_hash
                                            
                                            file_metadata = metadata.get("file_metadata")
                                            
                                            should_update, schema_changed = should_update_or_insert(existing_record, file_hash, schema_hash)
                                            
                                            if not should_update and existing_record:
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
                                                    "type": "manual_trigger",
                                                    "name": "api_trigger",
                                                    "run_id": run_id
                                                },
                                                "scan": {
                                                    "container": container_name,
                                                    "folder": folder_path
                                                }
                                            }
                                            
                                            # Insert/Update database
                                            conn = pymysql.connect(
                                                host=DB_CONFIG["host"],
                                                port=DB_CONFIG["port"],
                                                user=DB_CONFIG["user"],
                                                password=DB_CONFIG["password"],
                                                database=DB_CONFIG["database"],
                                                cursorclass=pymysql.cursors.DictCursor
                                            )
                                            try:
                                                with conn.cursor() as cursor:
                                                    if existing_record:
                                                        if schema_changed:
                                                            cursor.execute("""
                                                                UPDATE data_discovery
                                                                SET file_metadata = %s,
                                                                    schema_json = %s,
                                                                    schema_hash = %s,
                                                                    storage_metadata = %s,
                                                                    discovery_info = %s,
                                                                    last_checked_at = NOW(),
                                                                    updated_at = NOW()
                                                                WHERE id = %s
                                                            """, (
                                                                json.dumps(file_metadata),
                                                                json.dumps(metadata.get("schema_json", {})),
                                                                schema_hash,
                                                                json.dumps(metadata.get("storage_metadata", {})),
                                                                json.dumps(discovery_info),
                                                                existing_record["id"]
                                                            ))
                                                        else:
                                                            cursor.execute("""
                                                                UPDATE data_discovery
                                                                SET last_checked_at = NOW()
                                                                WHERE id = %s
                                                            """, (existing_record["id"],))
                                                    else:
                                                        cursor.execute("""
                                                            INSERT INTO data_discovery (
                                                                storage_location, file_metadata, schema_json, schema_hash,
                                                                discovered_at, status, approval_status, is_visible, is_active,
                                                                environment, env_type, data_source_type, folder_path,
                                                                storage_metadata, storage_data_metadata, discovery_info,
                                                                created_by
                                                            ) VALUES (
                                                                %s, %s, %s, %s,
                                                                NOW(), 'pending', 'pending_review', TRUE, TRUE,
                                                                %s, %s, %s, %s, %s, %s, %s, 'api_trigger'
                                                            )
                                                        """, (
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
                                                        all_new_discoveries.append({
                                                            "id": discovery_id,
                                                            "file_name": file_metadata["basic"]["name"],
                                                            "storage_path": blob_path,
                                                        })
                                                    
                                                    conn.commit()
                                            finally:
                                                conn.close()
                                        
                                        except Exception as e:
                                            logger.warning(f'FN:trigger_discovery blob error: {str(e)}')
                                            continue
                                
                                except Exception as e:
                                    logger.warning(f'FN:trigger_discovery folder error: {str(e)}')
                                    continue
                    
                    except Exception as e:
                        logger.warning(f'FN:trigger_discovery account error: {str(e)}')
                        continue
                
                logger.info(f'FN:trigger_discovery completed new_discoveries: {len(all_new_discoveries)}')
                
            except Exception as e:
                logger.error(f'FN:trigger_discovery thread error: {str(e)}')
        
        # Run discovery in background thread
        thread = threading.Thread(target=run_discovery, daemon=True)
        thread.start()
        
        return jsonify({
            'message': 'Discovery triggered successfully',
            'status': 'running'
        }), 202  # 202 Accepted - request accepted but processing not complete
        
    except Exception as e:
        logger.error(f'FN:trigger_discovery error:{str(e)}')
        return jsonify({'error': str(e)}), 500
