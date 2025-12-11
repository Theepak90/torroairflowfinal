from azure.storage.blob import BlobServiceClient, ContentSettings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AzureBlobClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    def list_blobs(self, container_name: str, folder_path: str = "", file_extensions: List[str] = None) -> List[Dict]:
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blobs = []
            
            prefix = folder_path.rstrip("/") + "/" if folder_path else ""
            blob_list = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blob_list:
                if file_extensions:
                    if not any(blob.name.lower().endswith(ext.lower()) for ext in file_extensions):
                        continue
                # Skip directories (blobs ending with /)
                if blob.name.endswith('/'):
                    continue
                
                blob_client = container_client.get_blob_client(blob.name)
                blob_properties = blob_client.get_blob_properties()
                
                blob_type = None
                if hasattr(blob_properties, 'blob_type'):
                    blob_type = blob_properties.blob_type
                elif hasattr(blob_properties, 'blob_tier'):
                    blob_type = "Block blob"
                else:
                    blob_type = "Block blob"
                
                blob_info = {
                    "name": blob.name.split("/")[-1],
                    "full_path": blob.name,
                    "size": blob_properties.size,
                    "content_type": blob_properties.content_settings.content_type,
                    "created_at": blob_properties.creation_time,
                    "last_modified": blob_properties.last_modified,
                    "etag": blob_properties.etag,
                    "blob_type": blob_type,
                    "access_tier": blob_properties.blob_tier if hasattr(blob_properties, 'blob_tier') else None,
                    "lease_status": blob_properties.lease.status if hasattr(blob_properties, 'lease') else None,
                    "content_encoding": blob_properties.content_settings.content_encoding,
                    "content_language": blob_properties.content_settings.content_language,
                    "cache_control": blob_properties.content_settings.cache_control,
                    "metadata": blob_properties.metadata,
                }
                
                blobs.append(blob_info)
            
            logger.info(f"Found {len(blobs)} blobs in container '{container_name}' folder '{folder_path}'")
            return blobs
            
        except Exception as e:
            logger.error(f"Error listing blobs: {str(e)}")
            raise
    
    def get_blob_content(self, container_name: str, blob_path: str) -> bytes:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_path
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading blob {blob_path}: {str(e)}")
            raise
    
    def get_blob_sample(self, container_name: str, blob_path: str, max_bytes: int = 1024) -> bytes:
        # Get only headers/column names (first N bytes) - NO data rows
        # For banking/financial compliance: We only extract column names, never actual data
        # CSV: First line only (headers)
        # JSON: First object keys only
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_path
            )
            # Download only first max_bytes (just enough for headers/keys - NO data)
            return blob_client.download_blob(offset=0, length=max_bytes).readall()
        except Exception as e:
            logger.warning(f"Error getting blob sample for {blob_path}: {str(e)}")
            return b""
    
    def get_blob_tail(self, container_name: str, blob_path: str, max_bytes: int = 8192) -> bytes:
        # Get the tail (last N bytes) of a blob. Useful for Parquet files where metadata is at the end
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_path
            )
            # Get file size first
            properties = blob_client.get_blob_properties()
            file_size = properties.size
            
            # Read from the end
            offset = max(0, file_size - max_bytes)
            length = min(max_bytes, file_size)
            return blob_client.download_blob(offset=offset, length=length).readall()
        except Exception as e:
            logger.warning(f"Error getting blob tail for {blob_path}: {str(e)}")
            return b""
    
    def get_blob_properties(self, container_name: str, blob_path: str) -> Dict:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_path
            )
            properties = blob_client.get_blob_properties()
            
            return {
                "etag": properties.etag,
                "size": properties.size,
                "content_type": properties.content_settings.content_type,
                "created_at": properties.creation_time,
                "last_modified": properties.last_modified,
                "access_tier": properties.blob_tier if hasattr(properties, 'blob_tier') else None,
                "lease_status": properties.lease.status if hasattr(properties, 'lease') else None,
                "content_encoding": properties.content_settings.content_encoding,
                "content_language": properties.content_settings.content_language,
                "cache_control": properties.content_settings.cache_control,
                "metadata": properties.metadata,
            }
        except Exception as e:
            logger.error(f"Error getting blob properties for {blob_path}: {str(e)}")
            raise
    
    def upload_blob(self, container_name: str, blob_path: str, content: bytes, content_type: str = "text/plain"):
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_path
            )
            content_settings = ContentSettings(content_type=content_type)
            blob_client.upload_blob(content, overwrite=True, content_settings=content_settings)
            logger.info(f"Uploaded blob {blob_path} to container {container_name}")
        except Exception as e:
            logger.error(f"Error uploading blob {blob_path}: {str(e)}")
            raise
