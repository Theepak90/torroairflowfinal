from typing import Dict, Optional, List
from datetime import datetime
import json


class DataDiscovery:
    @staticmethod
    def from_db_row(row: Dict) -> Dict:
        if not row:
            return None
        
        result = dict(row)
        json_fields = [
            'storage_location', 'file_metadata', 'schema_json', 'tags',
            'storage_metadata', 'storage_data_metadata', 'additional_metadata',
            'validation_errors', 'notification_recipients', 'discovery_info',
            'approval_workflow'
        ]
        for key in json_fields:
            if result.get(key) and isinstance(result[key], str):
                try:
                    result[key] = json.loads(result[key])
                except json.JSONDecodeError:
                    result[key] = {} if key not in ['tags', 'validation_errors', 'notification_recipients'] else []
        
        return result
