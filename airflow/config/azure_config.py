import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

AZURE_STORAGE_ACCOUNTS = [
    {
        "name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "myaccount"),
        "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
        "containers": [c.strip() for c in os.getenv("AZURE_CONTAINERS", "data-container").split(",") if c.strip()],
        "folders": [f.strip() for f in os.getenv("AZURE_FOLDERS", "folder/credit_card").split(",") if f.strip()],
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
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
}

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "torro_discovery"),
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
