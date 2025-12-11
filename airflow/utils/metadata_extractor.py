import hashlib
import json
import logging
from typing import Dict, Optional, List
import pyarrow.parquet as pq
import io
import csv
from collections import Counter
import re

logger = logging.getLogger(__name__)

# PII detection patterns
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
    "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
    "date_of_birth": re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
}

PII_COLUMN_KEYWORDS = {
    "email": ["email", "e-mail", "mail", "email_address"],
    "phone": ["phone", "mobile", "cell", "telephone", "contact"],
    "ssn": ["ssn", "social_security", "social security"],
    "credit_card": ["credit_card", "card_number", "cc_number", "card"],
    "name": ["first_name", "last_name", "full_name", "name", "fname", "lname"],
    "address": ["address", "street", "city", "zip", "postal"],
    "date_of_birth": ["dob", "date_of_birth", "birthdate", "birth_date"],
    "ip": ["ip", "ip_address", "ipaddress"],
}


def detect_pii_in_column(column_name: str, sample_values: List[str]) -> Dict[str, bool]:
    # Detect PII in a column based on column name and sample values
    # Returns a dict indicating which PII types are detected
    pii_detected = {pii_type: False for pii_type in PII_PATTERNS.keys()}
    pii_detected["name"] = False
    pii_detected["address"] = False
    
    column_lower = column_name.lower()
    
    # Check column name keywords
    for pii_type, keywords in PII_COLUMN_KEYWORDS.items():
        if any(keyword in column_lower for keyword in keywords):
            pii_detected[pii_type] = True
    
    # Check sample values for patterns
    for value in sample_values[:100]:  # Check first 100 values
        if not value or not isinstance(value, str):
            continue
        
        value_str = str(value).strip()
        if not value_str:
            continue
        
        # Check email
        if PII_PATTERNS["email"].search(value_str):
            pii_detected["email"] = True
        
        # Check phone
        if PII_PATTERNS["phone"].search(value_str):
            pii_detected["phone"] = True
        
        # Check SSN
        if PII_PATTERNS["ssn"].search(value_str):
            pii_detected["ssn"] = True
        
        # Check credit card
        if PII_PATTERNS["credit_card"].search(value_str):
            pii_detected["credit_card"] = True
        
        # Check IP address
        if PII_PATTERNS["ip_address"].search(value_str):
            pii_detected["ip"] = True
    
    return pii_detected


def generate_file_hash(file_content: bytes, algorithm: str = "sha256") -> str:
    if algorithm == "sha256":
        hash_obj = hashlib.sha256(file_content)
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    return hash_obj.hexdigest()


def extract_parquet_schema(file_content: bytes) -> Dict:
    # Extract Parquet schema from file content. Parquet metadata is at the end of the file
    # We need the tail of the file (last 8KB) which contains the schema metadata
    # This function should receive the tail bytes, not the head
    try:
        parquet_file = pq.ParquetFile(io.BytesIO(file_content))
        schema = parquet_file.schema_arrow
        
        columns = []
        # For Parquet, we only check column names for PII keywords (no data samples needed)
        # Column names are in the schema metadata
        for i in range(len(schema)):
            field = schema.field(i)
            pii_detected = detect_pii_in_column(field.name, [])  # Empty sample, only name check
            pii_types = [pii_type for pii_type, detected in pii_detected.items() if detected]
            
            columns.append({
                "name": field.name,
                "type": str(field.type),
                "nullable": field.nullable,
                "pii_detected": len(pii_types) > 0,
                "pii_types": pii_types if pii_types else None
            })
        
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
        logger.warning(f"Error extracting parquet schema: {str(e)}")
        return {"columns": [], "num_columns": 0}


def generate_schema_hash(schema_json: Dict) -> str:
    schema_str = json.dumps(schema_json, sort_keys=True)
    return hashlib.sha256(schema_str.encode()).hexdigest()


def extract_csv_schema(file_content: bytes, sample_size: int = 0) -> Dict:
    # Extract CSV schema from headers ONLY - no data rows downloaded
    # For banking/financial data: We only extract column names, never actual data
    # PII detection is based solely on column name keywords
    try:
        content_str = file_content.decode('utf-8', errors='ignore')
        lines = content_str.split('\n')
        
        if not lines:
            return {"columns": [], "num_columns": 0}
        
        # ONLY read first line (headers) - NO data rows
        reader = csv.reader([lines[0]])  # Only header line
        headers = next(reader, None)
        
        if not headers:
            return {"columns": [], "num_columns": 0}
        
        columns = []
        
        for i, header in enumerate(headers):
            header = header.strip()
            if not header:
                header = f"column_{i+1}"
            
            # NO data rows - only use column name for PII detection
            # Banking compliance: We don't download/process actual data
            pii_detected = detect_pii_in_column(header, [])  # Empty sample - only column name check
            pii_types = [pii_type for pii_type, detected in pii_detected.items() if detected]
            
            columns.append({
                "name": header,
                "type": "string",  # Default type since we don't have data samples
                "nullable": True,
                "pii_detected": len(pii_types) > 0,
                "pii_types": pii_types if pii_types else None
            })
        
        return {
            "columns": columns,
            "num_columns": len(columns),
            "num_rows": None,  # Don't know row count - we only have headers
            "has_header": True,
            "delimiter": ","
        }
        
    except Exception as e:
        logger.warning(f"Error extracting CSV schema: {str(e)}")
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
            # Single object - just get keys (column names), NO values processed
            for key in data.keys():
                # NO value processing - only column name for PII detection (banking compliance)
                pii_detected = detect_pii_in_column(str(key), [])  # Empty sample - only name check
                pii_types = [pii_type for pii_type, detected in pii_detected.items() if detected]
                
                columns.append({
                    "name": str(key),
                    "type": "string",  # Default type since we don't process values
                    "nullable": True,
                    "pii_detected": len(pii_types) > 0,
                    "pii_types": pii_types if pii_types else None
                })
        elif isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict):
                # Extract columns from first item keys ONLY - NO value processing
                for key in first_item.keys():
                    # NO value samples - only column name for PII detection (banking compliance)
                    pii_detected = detect_pii_in_column(str(key), [])  # Empty sample - only name check
                    pii_types = [pii_type for pii_type, detected in pii_detected.items() if detected]
                    
                    columns.append({
                        "name": str(key),
                        "type": "string",  # Default type since we don't process values
                        "nullable": True,
                        "pii_detected": len(pii_types) > 0,
                        "pii_types": pii_types if pii_types else None
                    })
            else:
                columns.append({
                    "name": "value",
                    "type": "string",
                    "nullable": True,
                    "pii_detected": False,
                    "pii_types": None
                })
        
        return {
            "columns": columns,
            "num_columns": len(columns),
            "structure": "object" if isinstance(data, dict) else "array",
            "num_items": len(data) if isinstance(data, list) else None
        }
        
    except Exception as e:
        logger.warning(f"Error extracting JSON schema: {str(e)}")
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
            "algorithm": "sha256",
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
            logger.warning(f"Error extracting parquet format info: {str(e)}")
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
            logger.warning(f"Error extracting schema from {file_name}: {str(e)}")
            schema_json = {}
            schema_hash = hashlib.sha256(b"").hexdigest()
    elif file_format == "csv" and file_content:
        try:
            schema_json = extract_csv_schema(file_content)
            schema_hash = generate_schema_hash(schema_json)
        except Exception as e:
            logger.warning(f"Error extracting CSV schema from {file_name}: {str(e)}")
            schema_json = {}
            schema_hash = hashlib.sha256(b"").hexdigest()
    elif file_format == "json" and file_content:
        try:
            schema_json = extract_json_schema(file_content)
            schema_hash = generate_schema_hash(schema_json)
        except Exception as e:
            logger.warning(f"Error extracting JSON schema from {file_name}: {str(e)}")
            schema_json = {}
            schema_hash = hashlib.sha256(b"").hexdigest()
    else:
        schema_json = {}
        schema_hash = hashlib.sha256(json.dumps({}).encode()).hexdigest()
    
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
    
    return {
        "file_metadata": file_metadata,
        "schema_json": schema_json,
        "schema_hash": schema_hash,
        "file_hash": file_hash,
        "storage_metadata": storage_metadata
    }
