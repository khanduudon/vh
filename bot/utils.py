"""
Utility functions for the ClassPlus Batch File Extractor
"""
import re
import mimetypes
from pathlib import Path
from typing import Optional
from bot.exceptions import ValidationError


def save_to_file(data, filename):
    """Save data to file (legacy function)"""
    with open(filename, 'w') as file:
        file.write(str(data))


def validate_org_code(org_code: str) -> bool:
    """
    Validate organization code format
    
    Args:
        org_code: Organization code to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If org code is invalid
    """
    if not org_code:
        raise ValidationError('org_code', org_code, 'Organization code cannot be empty')
    
    if not isinstance(org_code, str):
        raise ValidationError('org_code', org_code, 'Organization code must be a string')
    
    # Org code should be alphanumeric and 3-20 characters
    if not re.match(r'^[a-zA-Z0-9]{3,20}$', org_code):
        raise ValidationError(
            'org_code', 
            org_code, 
            'Organization code must be 3-20 alphanumeric characters'
        )
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_content_type(filename: str) -> str:
    """
    Get MIME content type from filename
    
    Args:
        filename: File name
        
    Returns:
        MIME content type
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or 'application/octet-stream'


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    
    # Limit filename length
    max_length = 255
    if len(filename) > max_length:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:max_length - len(ext)] + ext
    
    return filename


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: File name
        
    Returns:
        File extension (including dot)
    """
    return Path(filename).suffix.lower()


def is_allowed_file_type(filename: str, allowed_types: list) -> bool:
    """
    Check if file type is allowed
    
    Args:
        filename: File name
        allowed_types: List of allowed file extensions
        
    Returns:
        True if allowed, False otherwise
    """
    ext = get_file_extension(filename)
    return ext in [t.lower() for t in allowed_types]
