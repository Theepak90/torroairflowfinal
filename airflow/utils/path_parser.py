"""
Flexible path parser for different storage path formats.
This module provides extensible path parsing to support various storage path formats.
"""
import re
import logging
from typing import Dict, Optional, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PathParser(ABC):
    """Abstract base class for path parsers"""
    
    @abstractmethod
    def can_parse(self, path: str) -> bool:
        """Check if this parser can handle the given path"""
        pass
    
    @abstractmethod
    def parse(self, path: str) -> Dict[str, str]:
        """Parse the path and return structured information"""
        pass
    
    @abstractmethod
    def get_storage_type(self) -> str:
        """Return the storage type identifier"""
        pass


class ABFSPathParser(PathParser):
    """Parser for Azure Data Lake Storage Gen2 ABFS paths
    
    Supports:
    - abfs://filesystem@account.dfs.core.windows.net/path
    - abfss://filesystem@account.dfs.core.windows.net/path (secure)
    """
    
    def can_parse(self, path: str) -> bool:
        return path.startswith("abfs://") or path.startswith("abfss://")
    
    def parse(self, path: str) -> Dict[str, str]:
        try:
            # Remove protocol prefix
            if path.startswith("abfs://"):
                path = path[7:]
            elif path.startswith("abfss://"):
                path = path[8:]
            
            # Split by @ to get filesystem and rest
            if "@" not in path:
                raise ValueError("Invalid ABFS path format: missing @")
            
            filesystem, rest = path.split("@", 1)
            
            # Split by .dfs.core.windows.net to get account and path
            if ".dfs.core.windows.net" not in rest:
                raise ValueError("Invalid ABFS path format: missing .dfs.core.windows.net")
            
            account_and_path = rest.replace(".dfs.core.windows.net", "")
            
            # Account name is before first /
            if "/" in account_and_path:
                account_name, file_path = account_and_path.split("/", 1)
                file_path = file_path.lstrip("/")
            else:
                account_name = account_and_path
                file_path = ""
            
            return {
                "account_name": account_name,
                "filesystem": filesystem,
                "path": file_path,
                "full_path": path,
                "protocol": "abfs" if path.startswith("abfs://") else "abfss"
            }
        except Exception as e:
            logger.error('FN:ABFSPathParser.parse path:{} error:{}'.format(path, str(e)))
            raise ValueError(f"Failed to parse ABFS path: {str(e)}")
    
    def get_storage_type(self) -> str:
        return "azure_datalake"


class BlobPathParser(PathParser):
    """Parser for Azure Blob Storage paths
    
    Supports:
    - https://account.blob.core.windows.net/container/path
    - account/container/path
    """
    
    def can_parse(self, path: str) -> bool:
        return (
            "blob.core.windows.net" in path or
            (not path.startswith("abfs://") and not path.startswith("abfss://") and "/" in path)
        )
    
    def parse(self, path: str) -> Dict[str, str]:
        try:
            # Handle full URL format
            if "blob.core.windows.net" in path:
                # Extract from https://account.blob.core.windows.net/container/path
                match = re.match(r'https?://([^/]+)\.blob\.core\.windows\.net/([^/]+)(?:/(.*))?', path)
                if match:
                    account_name = match.group(1)
                    container = match.group(2)
                    file_path = match.group(3) or ""
                    return {
                        "account_name": account_name,
                        "container": container,
                        "path": file_path,
                        "full_path": path
                    }
            
            # Handle simple format: container/path or account/container/path
            parts = path.split("/", 2)
            if len(parts) == 3:
                # account/container/path
                return {
                    "account_name": parts[0],
                    "container": parts[1],
                    "path": parts[2],
                    "full_path": path
                }
            elif len(parts) == 2:
                # container/path (account not in path)
                return {
                    "account_name": "",  # Will be provided separately
                    "container": parts[0],
                    "path": parts[1],
                    "full_path": path
                }
            else:
                # Just container name
                return {
                    "account_name": "",
                    "container": parts[0],
                    "path": "",
                    "full_path": path
                }
        except Exception as e:
            logger.error('FN:BlobPathParser.parse path:{} error:{}'.format(path, str(e)))
            raise ValueError(f"Failed to parse Blob path: {str(e)}")
    
    def get_storage_type(self) -> str:
        return "azure_blob"


class S3PathParser(PathParser):
    """Parser for AWS S3 paths (for future use)
    
    Supports:
    - s3://bucket/path
    - https://bucket.s3.region.amazonaws.com/path
    """
    
    def can_parse(self, path: str) -> bool:
        return path.startswith("s3://") or "s3." in path.lower() or ".s3.amazonaws.com" in path.lower()
    
    def parse(self, path: str) -> Dict[str, str]:
        try:
            if path.startswith("s3://"):
                # s3://bucket/path
                path = path[5:]
                if "/" in path:
                    bucket, file_path = path.split("/", 1)
                else:
                    bucket = path
                    file_path = ""
                return {
                    "bucket": bucket,
                    "path": file_path,
                    "full_path": path
                }
            else:
                # https://bucket.s3.region.amazonaws.com/path
                match = re.match(r'https?://([^/]+)\.s3[^/]*\.amazonaws\.com(?:/(.*))?', path)
                if match:
                    bucket = match.group(1)
                    file_path = match.group(2) or ""
                    return {
                        "bucket": bucket,
                        "path": file_path,
                        "full_path": path
                    }
                raise ValueError("Invalid S3 path format")
        except Exception as e:
            logger.error('FN:S3PathParser.parse path:{} error:{}'.format(path, str(e)))
            raise ValueError(f"Failed to parse S3 path: {str(e)}")
    
    def get_storage_type(self) -> str:
        return "aws_s3"


class GCSPathParser(PathParser):
    """Parser for Google Cloud Storage paths (for future use)
    
    Supports:
    - gs://bucket/path
    - https://storage.googleapis.com/bucket/path
    """
    
    def can_parse(self, path: str) -> bool:
        return path.startswith("gs://") or "storage.googleapis.com" in path.lower()
    
    def parse(self, path: str) -> Dict[str, str]:
        try:
            if path.startswith("gs://"):
                # gs://bucket/path
                path = path[5:]
                if "/" in path:
                    bucket, file_path = path.split("/", 1)
                else:
                    bucket = path
                    file_path = ""
                return {
                    "bucket": bucket,
                    "path": file_path,
                    "full_path": path
                }
            else:
                # https://storage.googleapis.com/bucket/path
                match = re.match(r'https?://storage\.googleapis\.com/([^/]+)(?:/(.*))?', path)
                if match:
                    bucket = match.group(1)
                    file_path = match.group(2) or ""
                    return {
                        "bucket": bucket,
                        "path": file_path,
                        "full_path": path
                    }
                raise ValueError("Invalid GCS path format")
        except Exception as e:
            logger.error('FN:GCSPathParser.parse path:{} error:{}'.format(path, str(e)))
            raise ValueError(f"Failed to parse GCS path: {str(e)}")
    
    def get_storage_type(self) -> str:
        return "gcs"


class PathParserRegistry:
    """Registry for path parsers with automatic detection"""
    
    def __init__(self):
        self._parsers: list[PathParser] = []
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register default parsers in order of specificity"""
        # Most specific first
        self.register(ABFSPathParser())
        self.register(S3PathParser())
        self.register(GCSPathParser())
        self.register(BlobPathParser())  # Least specific, should be last
    
    def register(self, parser: PathParser):
        """Register a new path parser"""
        if parser not in self._parsers:
            self._parsers.append(parser)
            logger.info('FN:PathParserRegistry.register parser_type:{}'.format(type(parser).__name__))
    
    def parse(self, path: str) -> Dict[str, str]:
        """
        Parse a path using the first matching parser
        
        Returns:
            Dict with parsed path information including:
            - storage_type: Type of storage (azure_datalake, azure_blob, aws_s3, gcs, etc.)
            - parsed_data: Parser-specific data (account_name, container, path, etc.)
        """
        if not path or not path.strip():
            raise ValueError("Path cannot be empty")
        
        path = path.strip()
        
        # Try each parser in order
        for parser in self._parsers:
            if parser.can_parse(path):
                try:
                    parsed_data = parser.parse(path)
                    storage_type = parser.get_storage_type()
                    
                    result = {
                        "storage_type": storage_type,
                        "original_path": path,
                        **parsed_data
                    }
                    
                    logger.info('FN:PathParserRegistry.parse path:{} storage_type:{} parser:{}'.format(
                        path, storage_type, type(parser).__name__
                    ))
                    return result
                except Exception as e:
                    logger.warning('FN:PathParserRegistry.parse parser:{} path:{} error:{}'.format(
                        type(parser).__name__, path, str(e)
                    ))
                    continue
        
        # If no parser matched, raise error
        raise ValueError(f"No parser found for path format: {path}")


# Global registry instance
_path_parser_registry = None


def get_path_parser() -> PathParserRegistry:
    """Get the global path parser registry"""
    global _path_parser_registry
    if _path_parser_registry is None:
        _path_parser_registry = PathParserRegistry()
    return _path_parser_registry


def parse_storage_path(path: str) -> Dict[str, str]:
    """
    Convenience function to parse a storage path
    
    Example:
        result = parse_storage_path("abfs://container@account.dfs.core.windows.net/path")
        # Returns: {
        #     "storage_type": "azure_datalake",
        #     "account_name": "account",
        #     "filesystem": "container",
        #     "path": "path",
        #     ...
        # }
    """
    return get_path_parser().parse(path)


# Backward compatibility: Keep the old function name
def parse_abfs_path(abfs_path: str) -> Dict[str, str]:
    """
    Parse ABFS path (backward compatibility wrapper)
    
    DEPRECATED: Use parse_storage_path() instead for extensibility
    """
    parser = ABFSPathParser()
    if not parser.can_parse(abfs_path):
        raise ValueError(f"Path is not an ABFS path: {abfs_path}")
    return parser.parse(abfs_path)

