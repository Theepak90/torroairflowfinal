import os
from dotenv import load_dotenv
from pathlib import Path

# config.py is at: backend/app/config.py
# Need to go: config.py -> app -> backend
# So: parent.parent gets us to backend directory
# Use resolve() to get absolute path
config_file = Path(__file__).resolve()
env_path = config_file.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Set TMPDIR to a writable location to prevent gunicorn permission errors
# This ensures temp files (like PID files) can be created
if 'TMPDIR' not in os.environ:
    # Try common writable temp directories
    for temp_dir in ['/tmp', '/var/tmp', os.path.expanduser('~/tmp')]:
        if os.path.exists(temp_dir) and os.access(temp_dir, os.W_OK):
            os.environ['TMPDIR'] = temp_dir
            break
    else:
        # Fallback to system temp if available
        import tempfile
        os.environ['TMPDIR'] = tempfile.gettempdir()


def _get_int_env(key: str, default: str) -> int:
    """Safely get integer from environment variable with fallback to default"""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return int(default)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MySQL configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = _get_int_env('MYSQL_PORT', '3306')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'torro_discovery')
    
    # CORS origins - use environment variable or default to allow all
    cors_origins_str = os.getenv('CORS_ORIGINS', '*')
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',')] if cors_origins_str != '*' else ['*']
    
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100
    
    # MySQL Connection Pool Settings
    DB_POOL_MIN = _get_int_env('DB_POOL_MIN', '5')  # Minimum connections in pool
    DB_POOL_MAX = _get_int_env('DB_POOL_MAX', '20')  # Maximum connections in pool
    DB_POOL_RECYCLE = _get_int_env('DB_POOL_RECYCLE', '3600')  # Recycle connections after 1 hour
    
    # Backend Server Configuration
    BACKEND_PORT = _get_int_env('BACKEND_PORT', '5001')  # Backend server port


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
