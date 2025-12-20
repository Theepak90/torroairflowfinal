import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (parent directory)
# Clear any existing MySQL env vars first to ensure fresh load
for key in list(os.environ.keys()):
    if key.startswith('MYSQL_'):
        del os.environ[key]

# config.py is at: backend/app/config.py
# Need to go: config.py -> app -> backend -> project_root
# So: parent.parent.parent gets us to project root
# Use resolve() to get absolute path
config_file = Path(__file__).resolve()
env_path = config_file.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'torro_discovery')
    
    # CORS origins - use environment variable or default to allow all (for Nginx proxy)
    cors_origins_str = os.getenv('CORS_ORIGINS', '*')
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',')] if cors_origins_str != '*' else ['*']
    
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100
    
    # MySQL Connection Pool Settings
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', '5'))  # Minimum connections in pool
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', '20'))  # Maximum connections in pool
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '3600'))  # Recycle connections after 1 hour
    
    # Backend Server Configuration
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', '5001'))  # Backend server port


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
