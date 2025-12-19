import hashlib
import json
import logging
from typing import Dict, Optional, List
import pyarrow.parquet as pq
import io
import csv
from collections import Counter

logger = logging.getLogger(__name__)

# Import Azure DLP client for PII detection
try:
    from utils.azure_dlp_client import detect_pii_in_column
    AZURE_DLP_AVAILABLE = True
except ImportError:
    logger.warning('FN:metadata_extractor_import AZURE_DLP_AVAILABLE:{}'.format(False))
    AZURE_DLP_AVAILABLE = False
    
    def detect_pii_in_column(column_name: str) -> Dict:
        """Fallback when Azure DLP import fails - returns no PII"""
        return {"pii_detected": False, "pii_types": []}


def generate_file_hash(file_content: bytes) -> str:
    # Use SHAKE128 (128 bits) only for file hashing
    hash_obj = hashlib.shake_128(file_content)
    return hash_obj.hexdigest(16)  # 16 bytes = 128 bits


def extract_parquet_schema(file_content: bytes) -> Dict:
    # Extract Parquet schema from file content. Parquet metadata is at the end of the file
    # We need the tail of the file (last 8KB) which contains the schema metadata
    # This function should receive the tail bytes, not the head
    try:
        parquet_file = pq.ParquetFile(io.BytesIO(file_content))
        schema = parquet_file.schema_arrow
        
        columns = []
        for i in range(len(schema)):
            field = schema.field(i)
            # Detect PII using Azure DLP
            pii_result = detect_pii_in_column(field.name)
            
            column_data = {
                "name": field.name,
                "type": str(field.type),
                "nullable": field.nullable
            }
            
            # Add PII detection results if available
            if AZURE_DLP_AVAILABLE and pii_result.get("pii_detected"):
                column_data["pii_detected"] = True
                column_data["pii_types"] = pii_result.get("pii_types", [])
            else:
                column_data["pii_detected"] = False
                column_data["pii_types"] = None
            
            columns.append(column_data)
        
        schema_dict = {
            "columns": columns,
            "num_columns": len(columns),
        }
        
        try:
            metadata = parquet_file.metadata
            if metadata and hasattr(metadata, 'num_rows'):
                schema_dict["num_rows"] = metadata.num_rows
        except:
            pass
        
        return schema_dict
        
    except Exception as e:
        logger.warning('FN:extract_parquet_schema file_content_size:{} error:{}'.format(len(file_content) if file_content else 0, str(e)))
        return {"columns": [], "num_columns": 0}


def generate_schema_hash(schema_json: Dict) -> str:
    schema_str = json.dumps(schema_json, sort_keys=True)
    hash_obj = hashlib.shake_128(schema_str.encode())
    return hash_obj.hexdigest(16)  # 16 bytes = 128 bits


def extract_csv_schema(file_content: bytes, sample_size: int = 0) -> Dict:
    # Extract CSV schema from headers + 1-2 sample rows for reference
    # For banking/financial compliance: Minimal data exposure - only 1-2 rows for type inference
    try:
        content_str = file_content.decode('utf-8', errors='ignore')
        lines = [line for line in content_str.split('\n') if line.strip()]  # Remove empty lines
        
        if not lines:
            return {"columns": [], "num_columns": 0}
        
        # Read header (first line)
        reader = csv.reader([lines[0]])
        headers = next(reader, None)
        
        if not headers:
            return {"columns": [], "num_columns": 0}
        
        # Get 1-2 sample rows for type inference (banking compliance: minimal data)
        sample_rows = []
        if len(lines) > 1:
            # Get up to 2 sample rows (skip header)
            for line in lines[1:3]:  # Max 2 sample rows
                try:
                    row_reader = csv.reader([line])
                    row = next(row_reader, None)
                    if row:
                        sample_rows.append(row)
                except:
                    pass
        
        columns = []
        
        for i, header in enumerate(headers):
            header = header.strip()
            if not header:
                header = f"column_{i+1}"
            
            # Get sample values from 1-2 rows for this column (for type inference only)
            sample_values = []
            for row in sample_rows:
                if i < len(row):
                    sample_values.append(row[i].strip() if row[i] else "")
            
            # Infer type from sample values (1-2 rows only)
            inferred_type = infer_column_type(sample_values) if sample_values else "string"
            
            # Detect PII using Azure DLP
            pii_result = detect_pii_in_column(header)
            
            column_data = {
                "name": header,
                "type": inferred_type,
                "nullable": True
            }
            
            # Add PII detection results if available
            if AZURE_DLP_AVAILABLE and pii_result.get("pii_detected"):
                column_data["pii_detected"] = True
                column_data["pii_types"] = pii_result.get("pii_types", [])
            else:
                column_data["pii_detected"] = False
                column_data["pii_types"] = None
            
            # Add sample values for reference (1-2 rows only - banking compliant)
            if sample_values:
                column_data["sample_values"] = sample_values[:2]  # Max 2 sample values
            
            columns.append(column_data)
        
        return {
            "columns": columns,
            "num_columns": len(columns),
            "num_rows": None,  # Don't know total row count
            "has_header": True,
            "delimiter": ",",
            "sample_rows_count": len(sample_rows)  # 0, 1, or 2
        }
        
    except Exception as e:
        logger.warning('FN:extract_csv_schema file_content_size:{} sample_size:{} error:{}'.format(len(file_content) if file_content else 0, sample_size, str(e)))
        return {"columns": [], "num_columns": 0}


def infer_column_type(values: List[str]) -> str:
    if not values:
        return "string"
    
    non_empty = [v.strip() for v in values if v and v.strip()]
    if not non_empty:
        return "string"
    
    int_count = 0
    float_count = 0
    bool_count = 0
    date_count = 0
    
    for value in non_empty[:100]:
        value = value.strip()
        
        if value.lower() in ['true', 'false', 'yes', 'no', '1', '0']:
            bool_count += 1
        
        try:
            int(value)
            int_count += 1
        except ValueError:
            pass
        
        try:
            float(value)
            float_count += 1
        except ValueError:
            pass
        
        if '/' in value or '-' in value:
            parts = value.replace('/', '-').split('-')
            if len(parts) == 3:
                try:
                    int(parts[0])
                    int(parts[1])
                    int(parts[2])
                    date_count += 1
                except ValueError:
                    pass
    
    total = len(non_empty)
    threshold = total * 0.8
    
    if int_count >= threshold:
        return "int64"
    elif float_count >= threshold:
        return "double"
    elif bool_count >= threshold:
        return "bool"
    elif date_count >= threshold:
        return "date"
    else:
        return "string"


def extract_json_schema(file_content: bytes) -> Dict:
    # Extract JSON schema with 1-2 sample values for reference (banking compliance)
    try:
        content_str = file_content.decode('utf-8', errors='ignore').strip()
        
        if not content_str:
            return {"columns": [], "num_columns": 0}
        
        try:
            data = json.loads(content_str)
        except json.JSONDecodeError:
            return {"columns": [], "num_columns": 0, "error": "Invalid JSON"}
        
        columns = []
        
        if isinstance(data, dict):
            # Single object - get keys + 1 sample value per key for type inference
            for key in data.keys():
                value = data.get(key)
                inferred_type = infer_json_type(value)
                
                # Detect PII using Azure DLP
                pii_result = detect_pii_in_column(str(key))
                
                column_data = {
                    "name": str(key),
                    "type": inferred_type,
                    "nullable": value is None
                }
                
                # Add 1 sample value for reference (banking compliant - minimal data)
                if value is not None:
                    # Convert to string, truncate if too long (max 100 chars)
                    sample_val = str(value)
                    if len(sample_val) > 100:
                        sample_val = sample_val[:100] + "..."
                    column_data["sample_value"] = sample_val
                
                # Add PII detection results if available
                if AZURE_DLP_AVAILABLE and pii_result.get("pii_detected"):
                    column_data["pii_detected"] = True
                    column_data["pii_types"] = pii_result.get("pii_types", [])
                else:
                    column_data["pii_detected"] = False
                    column_data["pii_types"] = None
                
                columns.append(column_data)
        elif isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict):
                # Extract columns from first 1-2 items for sample values
                sample_items = data[:2]  # Max 2 items for reference
                
                for key in first_item.keys():
                    # Get sample values from 1-2 items
                    sample_values = []
                    for item in sample_items:
                        if isinstance(item, dict) and key in item:
                            val = item[key]
                            if val is not None:
                                sample_val = str(val)
                                if len(sample_val) > 100:
                                    sample_val = sample_val[:100] + "..."
                                sample_values.append(sample_val)
                    
                    # Infer type from first item
                    inferred_type = infer_json_type(first_item.get(key))
                    
                    # Detect PII using Azure DLP
                    pii_result = detect_pii_in_column(str(key))
                    
                    column_data = {
                        "name": str(key),
                        "type": inferred_type,
                        "nullable": first_item.get(key) is None
                    }
                    
                    # Add sample values (1-2 items only - banking compliant)
                    if sample_values:
                        column_data["sample_values"] = sample_values[:2]
                    
                    # Add PII detection results if available
                    if AZURE_DLP_AVAILABLE and pii_result.get("pii_detected"):
                        column_data["pii_detected"] = True
                        column_data["pii_types"] = pii_result.get("pii_types", [])
                    else:
                        column_data["pii_detected"] = False
                        column_data["pii_types"] = None
                    
                    columns.append(column_data)
            else:
                columns.append({
                    "name": "value",
                    "type": infer_json_type(first_item),
                    "nullable": False,
                    "pii_detected": False,
                    "pii_types": None,
                    "sample_values": [str(data[i])[:100] for i in range(min(2, len(data)))]
                })
        
        return {
            "columns": columns,
            "num_columns": len(columns),
            "structure": "object" if isinstance(data, dict) else "array",
            "num_items": len(data) if isinstance(data, list) else None
        }
        
    except Exception as e:
        logger.warning('FN:extract_json_schema file_content_size:{} error:{}'.format(len(file_content) if file_content else 0, str(e)))
        return {"columns": [], "num_columns": 0}


def infer_json_type(value) -> str:
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int64"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        if len(value) > 0:
            return f"array<{infer_json_type(value[0])}>"
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "string"


def extract_file_metadata(blob_info: Dict, file_content: Optional[bytes] = None) -> Dict:
    from datetime import datetime
    
    file_name = blob_info["name"]
    file_extension = "." + file_name.split(".")[-1] if "." in file_name else ""
    file_format = file_extension[1:].lower() if file_extension else "unknown"
    
    file_hash = None
    if file_content:
        file_hash = generate_file_hash(file_content)
    else:
        file_hash = generate_file_hash(b"")
    
    file_metadata = {
        "basic": {
            "name": file_name,
            "extension": file_extension,
            "format": file_format,
            "size_bytes": blob_info["size"],
            "content_type": blob_info.get("content_type", "application/octet-stream"),
            "mime_type": blob_info.get("content_type", "application/octet-stream")
        },
        "hash": {
            "algorithm": "shake128",
            "value": file_hash,
            "computed_at": datetime.utcnow().isoformat() + "Z"
        },
        "timestamps": {
            "created_at": blob_info["created_at"].isoformat() if blob_info.get("created_at") else None,
            "last_modified": blob_info["last_modified"].isoformat() if blob_info.get("last_modified") else None
        }
    }
    
    format_specific = {}
    if file_format == "parquet" and file_content:
        try:
            parquet_schema = extract_parquet_schema(file_content)
            format_specific["parquet"] = {
                "row_groups": parquet_schema.get("num_rows", 0),
                "compression": "unknown",
                "schema_version": "1.0"
            }
        except Exception as e:
            logger.warning('FN:extract_file_metadata file_name:{} file_format:{} error:{}'.format(file_name, file_format, str(e)))
    elif file_format == "csv":
        format_specific["csv"] = {
            "delimiter": ",",
            "has_header": True,
            "encoding": "utf-8"
        }
    elif file_format == "json":
        format_specific["json"] = {
            "format": "unknown"
        }
    
    if format_specific:
        file_metadata["format_specific"] = format_specific
    
    schema_json = None
    schema_hash = None
    
    if file_format == "parquet" and file_content:
        try:
            schema_json = extract_parquet_schema(file_content)
            schema_hash = generate_schema_hash(schema_json)
        except Exception as e:
            logger.warning('FN:extract_file_metadata file_name:{} file_format:{} error:{}'.format(file_name, file_format, str(e)))
            schema_json = {}
            schema_hash = hashlib.shake_128(b"").hexdigest(16)  # 16 bytes = 128 bits
    elif file_format == "csv" and file_content:
        try:
            schema_json = extract_csv_schema(file_content)
            schema_hash = generate_schema_hash(schema_json)
        except Exception as e:
            logger.warning('FN:extract_file_metadata file_name:{} file_format:{} error:{}'.format(file_name, file_format, str(e)))
            schema_json = {}
            schema_hash = hashlib.shake_128(b"").hexdigest(16)  # 16 bytes = 128 bits
    elif file_format == "json" and file_content:
        try:
            schema_json = extract_json_schema(file_content)
            schema_hash = generate_schema_hash(schema_json)
        except Exception as e:
            logger.warning('FN:extract_file_metadata file_name:{} file_format:{} error:{}'.format(file_name, file_format, str(e)))
            schema_json = {}
            schema_hash = hashlib.shake_128(b"").hexdigest(16)  # 16 bytes = 128 bits
    else:
        schema_json = {}
        schema_hash = hashlib.shake_128(json.dumps({}).encode()).hexdigest(16)  # 16 bytes = 128 bits
    
    storage_metadata = {
        "azure": {
            "type": blob_info.get("blob_type", "Block blob"),
            "etag": blob_info.get("etag", "").strip('"') if blob_info.get("etag") else None,
            "access_tier": blob_info.get("access_tier"),
            "creation_time": blob_info.get("created_at").isoformat() if blob_info.get("created_at") else None,
            "last_modified": blob_info.get("last_modified").isoformat() if blob_info.get("last_modified") else None,
            "lease_status": blob_info.get("lease_status"),
            "content_encoding": blob_info.get("content_encoding"),
            "content_language": blob_info.get("content_language"),
            "cache_control": blob_info.get("cache_control"),
            "metadata": blob_info.get("metadata", {})
        }
    }
    
    # Structure metadata into 4 categories for frontend display
    structured_metadata = {
        "technical_metadata": {
            "file_system": {
                "name": file_metadata["basic"]["name"],
                "extension": file_metadata["basic"]["extension"],
                "format": file_metadata["basic"]["format"],
                "size_bytes": file_metadata["basic"]["size_bytes"],
                "mime_type": file_metadata["basic"]["mime_type"],
                "content_type": file_metadata["basic"]["content_type"]
            },
            "hash": {
                "algorithm": file_metadata["hash"]["algorithm"],
                "value": file_hash,
                "computed_at": file_metadata["hash"]["computed_at"]
            },
            "timestamps": file_metadata["timestamps"],
            "format_specific": format_specific,
            "storage": {
                "type": storage_metadata["azure"]["type"],
                "etag": storage_metadata["azure"]["etag"],
                "access_tier": storage_metadata["azure"]["access_tier"],
                "lease_status": storage_metadata["azure"]["lease_status"],
                "content_encoding": storage_metadata["azure"]["content_encoding"],
                "content_language": storage_metadata["azure"]["content_language"],
                "cache_control": storage_metadata["azure"]["cache_control"]
            }
        },
        "operational_metadata": {
            "discovery": {
                "discovered_at": None,  # Will be set by DAG
                "last_checked_at": None,  # Will be set by DAG
                "discovery_batch_id": None,  # Will be set by DAG
                "schema_version": None,
                "schema_hash": schema_hash
            },
            "status": {
                "current_status": "pending",  # Will be set by DAG
                "approval_status": None,
                "is_visible": True,
                "is_active": True
            },
            "workflow": {
                "notification_sent_at": None,
                "notification_recipients": [],
                "approval_workflow": None
            }
        },
        "business_metadata": {
            "context": {
                "environment": None,  # Will be set by DAG
                "env_type": None,  # Will be set by DAG
                "data_source_type": None,  # Will be set by DAG
                "folder_path": None  # Will be set by DAG
            },
            "classification": {
                "tags": [],
                "data_classification": None,
                "sensitivity_level": None
            },
            "storage_location": {
                "container": None,  # Will be set by DAG
                "account_name": None,  # Will be set by DAG
                "full_path": None  # Will be set by DAG
            }
        },
        "schema_pii": {
            "schema": schema_json if schema_json else {},
            "pii_summary": {
                "total_columns": schema_json.get("num_columns", 0) if schema_json else 0,
                "pii_columns_count": 0,
                "pii_types_found": [],
                "columns_with_pii": []
            }
        }
    }
    
    # Calculate PII summary if schema exists and determine data classification
    data_classification = "Internal"  # Default classification
    if schema_json and schema_json.get("columns"):
        pii_columns = []
        pii_types_set = set()
        for col in schema_json["columns"]:
            if col.get("pii_detected"):
                pii_columns.append({
                    "column_name": col.get("name"),
                    "pii_types": col.get("pii_types", [])
                })
                if col.get("pii_types"):
                    pii_types_set.update(col.get("pii_types", []))
        
        pii_count = len(pii_columns)
        pii_types_list = list(pii_types_set)
        
        structured_metadata["schema_pii"]["pii_summary"] = {
            "total_columns": schema_json.get("num_columns", 0),
            "pii_columns_count": pii_count,
            "pii_types_found": pii_types_list,
            "columns_with_pii": pii_columns
        }
        
        # Determine data classification based on PII detection
        if pii_count > 0:
            # Check for highly sensitive PII types
            sensitive_types = ["CreditCardNumber", "SSN", "PassportNumber", "DriverLicense", "BankAccount", "Email", "PhoneNumber"]
            has_sensitive_pii = any(pii_type in sensitive_types for pii_type in pii_types_list)
            
            if has_sensitive_pii:
                data_classification = "Confidential"  # Highly sensitive PII found
            else:
                data_classification = "Restricted"  # PII found but less sensitive
        else:
            data_classification = "Internal"  # No PII detected
    
    # Set data classification in business metadata
    structured_metadata["business_metadata"]["classification"]["data_classification"] = data_classification
    
    # Return both old format (for backward compatibility) and new structured format
    return {
        "file_metadata": file_metadata,
        "schema_json": schema_json,
        "schema_hash": schema_hash,
        "file_hash": file_hash,
        "storage_metadata": storage_metadata,
        "structured_metadata": structured_metadata  # New structured format
    }
