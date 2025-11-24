"""
Logging configuration for the ClassPlus Batch File Extractor
"""
import logging
import sys
from pathlib import Path
from bot.config import LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str = __name__, log_file: str = LOG_FILE) -> logging.Logger:
    """
    Set up and configure a logger with both file and console handlers
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_api_request(logger: logging.Logger, method: str, url: str, **kwargs):
    """Log API request details"""
    logger.debug(f"API Request: {method} {url}", extra={'kwargs': kwargs})


def log_api_response(logger: logging.Logger, status_code: int, url: str, duration: float):
    """Log API response details"""
    logger.debug(f"API Response: {status_code} from {url} (took {duration:.2f}s)")


def log_file_operation(logger: logging.Logger, operation: str, filename: str, size: int = None):
    """Log file operation details"""
    msg = f"File {operation}: {filename}"
    if size:
        msg += f" ({size} bytes)"
    logger.info(msg)


# Create default logger
default_logger = setup_logger('bot')
