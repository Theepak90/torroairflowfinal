import os
from typing import Dict
from dotenv import load_dotenv
from pathlib import Path

# Load .env from airflow directory
# config/azure_config.py is at: airflow/config/azure_config.py
# Need to go: config -> airflow
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Azure Authentication Method: "connection_string" or "service_principal"
AZURE_AUTH_METHOD = os.getenv("AZURE_AUTH_METHOD", "connection_string")

# Azure Storage Type: "blob" or "datalake"
# AZURE_STORAGE_TYPE = os.getenv("AZURE_STORAGE_TYPE", "blob")
AZURE_STORAGE_TYPE = "blob"  # Force blob storage for testing

# Parse Data Lake Storage Gen2 ABFS paths if provided
# Format: abfs://filesystem@account.dfs.core.windows.net/path
# AZURE_DATALAKE_PATHS = [p.strip() for p in os.getenv("AZURE_DATALAKE_PATHS", "").split(",") if p.strip()]
AZURE_DATALAKE_PATHS = []  # Commented out - using blob storage

AZURE_STORAGE_ACCOUNTS = [
    {
        "name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "myaccount"),
        "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
        # Service Principal credentials (for IT team provisioned account)
        "client_id": os.getenv("AZURE_CLIENT_ID", ""),
        "client_secret": os.getenv("AZURE_CLIENT_SECRET", ""),
        "tenant_id": os.getenv("AZURE_TENANT_ID", ""),
        "auth_method": AZURE_AUTH_METHOD,  # "connection_string" or "service_principal"
        "storage_type": AZURE_STORAGE_TYPE,  # "blob" or "datalake"
        "containers": [c.strip() for c in os.getenv("AZURE_CONTAINERS", "").split(",") if c.strip()],  # Empty = scan all containers
        "folders": [f.strip() for f in os.getenv("AZURE_FOLDERS", "").split(",") if f.strip()],  # Empty = scan root of containers
        # "datalake_paths": AZURE_DATALAKE_PATHS,  # ABFS paths for Data Lake Storage - COMMENTED OUT
        "datalake_paths": [],  # Commented out - using blob storage
        "environment": os.getenv("AZURE_ENVIRONMENT", "prod"),
        "env_type": os.getenv("AZURE_ENV_TYPE", "production"),
        "data_source_type": os.getenv("AZURE_DATA_SOURCE_TYPE", "credit_card"),
        "file_extensions": None,  # None = discover all files
    }
]

DISCOVERY_CONFIG = {
    "schedule_interval": "*/1 * * * *",
    "notification_recipients": [email.strip() for email in os.getenv("NOTIFICATION_EMAILS", "").split(",") if email.strip()],
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT") or "587"),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
}

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "torro_discovery"),
}

# Azure AI Language (DLP) Configuration
AZURE_AI_LANGUAGE_CONFIG = {
    "endpoint": os.getenv("AZURE_AI_LANGUAGE_ENDPOINT", ""),
    "key": os.getenv("AZURE_AI_LANGUAGE_KEY", ""),
    "enabled": bool(os.getenv("AZURE_AI_LANGUAGE_ENDPOINT") and os.getenv("AZURE_AI_LANGUAGE_KEY"))
}

def get_storage_location_json(account_name: str, container: str, blob_path: str) -> Dict:
    return {
        "type": "azure_blob",
        "path": blob_path,
        "connection": {
            "method": "connection_string",
            "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
            "account_name": account_name
        },
        "container": {
            "name": container,
            "type": "blob_container"
        },
        "metadata": {}
    }
