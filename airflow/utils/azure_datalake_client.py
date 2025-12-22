from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import ClientSecretCredential
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Import flexible path parser (backward compatible)
try:
    from utils.path_parser import parse_storage_path, parse_abfs_path
except ImportError:
    # Fallback if path_parser not available
    def parse_abfs_path(abfs_path: str) -> Dict[str, str]:
        """Fallback parser for backward compatibility"""
        if abfs_path.startswith("abfs://"):
            abfs_path = abfs_path[7:]
        elif abfs_path.startswith("abfss://"):
            abfs_path = abfs_path[8:]
        
        if "@" not in abfs_path:
            raise ValueError("Invalid ABFS path format: missing @")
        
        filesystem, rest = abfs_path.split("@", 1)
        
        if ".dfs.core.windows.net" not in rest:
            raise ValueError("Invalid ABFS path format: missing .dfs.core.windows.net")
        
        account_and_path = rest.replace(".dfs.core.windows.net", "")
        if "/" in account_and_path:
            account_name, path = account_and_path.split("/", 1)
            path = path.lstrip("/")
        else:
            account_name = account_and_path
            path = ""
        
        return {
            "account_name": account_name,
            "filesystem": filesystem,
            "path": path
        }


class AzureDataLakeClient:
    def __init__(self, account_name: str = None, 
                 client_id: str = None, client_secret: str = None, tenant_id: str = None,
                 account_url: str = None):
        """
        Initialize Azure Data Lake Storage Gen2 Client with service principal
        
        Args:
            account_name: Storage account name
            client_id: Service principal client ID
            client_secret: Service principal client secret
            tenant_id: Azure AD tenant ID
            account_url: Full account URL (alternative to account_name)
        """
        if account_url:
            account_url_final = account_url
        elif account_name:
            account_url_final = f"https://{account_name}.dfs.core.windows.net"
        else:
            raise ValueError("Either account_name or account_url must be provided")
        
        if client_id and client_secret and tenant_id:
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                additionally_allowed_tenants=["*"]  # Allow cross-tenant access
            )
            self.data_lake_service_client = DataLakeServiceClient(account_url=account_url_final, credential=credential)
            logger.info('FN:AzureDataLakeClient auth_method:service_principal account_url:{}'.format(account_url_final))
        else:
            raise ValueError("Service principal credentials (client_id, client_secret, tenant_id) must be provided")
    
    def list_filesystems(self) -> List[str]:
        """List all file system names in the storage account"""
        try:
            filesystems = []
            filesystem_list = self.data_lake_service_client.list_file_systems()
            for filesystem in filesystem_list:
                filesystems.append(filesystem.name)
            logger.info('FN:list_filesystems filesystem_count:{}'.format(len(filesystems)))
            return filesystems
        except Exception as e:
            logger.error('FN:list_filesystems error:{}'.format(str(e)))
            raise
    
    def list_paths(self, filesystem_name: str, directory_path: str = "", recursive: bool = True) -> List[Dict]:
        """
        List all paths (files and directories) in a file system
        
        Args:
            filesystem_name: Name of the file system (container)
            directory_path: Directory path to list (empty for root)
            recursive: Whether to list recursively
        """
        try:
            file_system_client = self.data_lake_service_client.get_file_system_client(filesystem_name)
            paths = []
            
            # Normalize path
            directory_path = directory_path.lstrip("/")
            
            try:
                path_list = file_system_client.get_paths(path=directory_path, recursive=recursive)
                path_items = []
                count = 0
                for path in path_list:
                    path_items.append(path)
                    count += 1
                    # Safety limit
                    if count > 10000:
                        logger.warning('FN:list_paths filesystem_name:{} directory_path:{} hit_safety_limit:10000'.format(filesystem_name, directory_path))
                        break
                logger.info('FN:list_paths filesystem_name:{} directory_path:{} fetched_path_count:{}'.format(filesystem_name, directory_path, len(path_items)))
            except Exception as e:
                logger.error('FN:list_paths filesystem_name:{} directory_path:{} list_error:{}'.format(filesystem_name, directory_path, str(e)))
                raise
            
            for path_item in path_items:
                # Skip directories (is_directory=True)
                if path_item.is_directory:
                    continue
                
                # Extract file name from path
                path_name = path_item.name
                file_name = path_name.split("/")[-1] if "/" in path_name else path_name
                
                path_info = {
                    "name": file_name,
                    "full_path": path_name,
                    "size": path_item.content_length if hasattr(path_item, 'content_length') else 0,
                    "content_type": getattr(path_item, 'content_type', 'application/octet-stream'),
                    "created_at": path_item.creation_time if hasattr(path_item, 'creation_time') else None,
                    "last_modified": path_item.last_modified if hasattr(path_item, 'last_modified') else None,
                    "etag": path_item.etag if hasattr(path_item, 'etag') else '',
                    "blob_type": "Data Lake File",
                    "access_tier": None,
                    "lease_status": None,
                    "content_encoding": None,
                    "content_language": None,
                    "cache_control": None,
                    "metadata": path_item.metadata if hasattr(path_item, 'metadata') else {},
                }
                
                paths.append(path_info)
            
            logger.info('FN:list_paths filesystem_name:{} directory_path:{} path_count:{}'.format(filesystem_name, directory_path, len(paths)))
            return paths
            
        except Exception as e:
            logger.error('FN:list_paths filesystem_name:{} directory_path:{} error:{}'.format(filesystem_name, directory_path, str(e)))
            raise
    
    def get_file_content(self, filesystem_name: str, file_path: str) -> bytes:
        """Get file content from Data Lake Storage"""
        try:
            file_client = self.data_lake_service_client.get_file_client(
                file_system=filesystem_name,
                file_path=file_path
            )
            return file_client.download_file().readall()
        except Exception as e:
            logger.error('FN:get_file_content filesystem_name:{} file_path:{} error:{}'.format(filesystem_name, file_path, str(e)))
            raise
    
    def get_file_sample(self, filesystem_name: str, file_path: str, max_bytes: int = 2048) -> bytes:
        """Get sample content from file (first N bytes)"""
        try:
            file_client = self.data_lake_service_client.get_file_client(
                file_system=filesystem_name,
                file_path=file_path
            )
            # Download first max_bytes
            return file_client.download_file(offset=0, length=max_bytes).readall()
        except Exception as e:
            logger.warning('FN:get_file_sample filesystem_name:{} file_path:{} max_bytes:{} error:{}'.format(filesystem_name, file_path, max_bytes, str(e)))
            return b""
    
    def get_file_properties(self, filesystem_name: str, file_path: str) -> Dict:
        """Get file properties from Data Lake Storage"""
        try:
            file_client = self.data_lake_service_client.get_file_client(
                file_system=filesystem_name,
                file_path=file_path
            )
            properties = file_client.get_file_properties()
            
            return {
                "etag": properties.etag,
                "size": properties.size,
                "content_type": getattr(properties, 'content_type', 'application/octet-stream'),
                "created_at": properties.creation_time if hasattr(properties, 'creation_time') else None,
                "last_modified": properties.last_modified,
                "access_tier": None,
                "lease_status": None,
                "content_encoding": None,
                "content_language": None,
                "cache_control": None,
                "metadata": properties.metadata if hasattr(properties, 'metadata') else {},
            }
        except Exception as e:
            logger.error('FN:get_file_properties filesystem_name:{} file_path:{} error:{}'.format(filesystem_name, file_path, str(e)))
            raise

