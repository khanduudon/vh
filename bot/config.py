"""
Configuration settings for ClassPlus Batch File Extractor
"""
import os
from pathlib import Path

# Database Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "classplus_extractor")

# Collections
COLLECTION_ORG_CODES = "org_codes"
COLLECTION_BATCH_FILES = "batch_files"

# ClassPlus API Configuration
CLASSPLUS_BASE_URL = os.getenv("CLASSPLUS_BASE_URL", "https://api.classplusapp.com")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))  # requests per minute
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds

# File Storage Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024)))  # 100 MB
ALLOWED_FILE_TYPES = ['.pdf', '.mp4', '.zip', '.txt', '.doc', '.docx', '.ppt', '.pptx']

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
CACHE_DIR = Path(os.getenv("CACHE_DIR", "./cache/batch_files"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour in seconds

# Ensure cache directory exists
if CACHE_ENABLED:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "extractor.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Parallel Download Configuration
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5"))
DOWNLOAD_CHUNK_SIZE = int(os.getenv("DOWNLOAD_CHUNK_SIZE", str(8 * 1024)))  # 8 KB

# Security
VALIDATE_SSL = os.getenv("VALIDATE_SSL", "True").lower() == "true"
