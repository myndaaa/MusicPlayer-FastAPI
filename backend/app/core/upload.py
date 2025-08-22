"""
Upload utilities for file handling, validation, and security.
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

AUDIO_MIME_TYPES = {
    'audio/mpeg': '.mp3',
    'audio/wav': '.wav',
    'audio/flac': '.flac',
    'audio/x-flac': '.flac'
}

IMAGE_MIME_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp'
}


def validate_upload_file(file: UploadFile, allowed_extensions: set, max_size: int) -> Tuple[bool, str]:
    """
    Validate uploaded file for type, size, and security.
    
    Args:
        file: FastAPI UploadFile object
        allowed_extensions: Set of allowed file extensions
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if hasattr(file, 'size') and file.size and file.size > max_size:
        return False, f"File too large. Maximum size is {max_size // (1024*1024)}MB"
    
    if not file.filename:
        return False, "No filename provided"
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
    
    if file.content_type:
        if file_ext in ALLOWED_AUDIO_EXTENSIONS:
            if file.content_type not in AUDIO_MIME_TYPES:
                return False, f"Invalid audio content type: {file.content_type}"
            expected_ext = AUDIO_MIME_TYPES[file.content_type]
            if file_ext != expected_ext:
                return False, f"Content type doesn't match extension. Expected: {expected_ext}"
        
        elif file_ext in ALLOWED_IMAGE_EXTENSIONS:
            if file.content_type not in IMAGE_MIME_TYPES:
                return False, f"Invalid image content type: {file.content_type}"
            expected_ext = IMAGE_MIME_TYPES[file.content_type]
            if file_ext != expected_ext:
                return False, f"Content type doesn't match extension. Expected: {expected_ext}"
    
    return True, ""


def get_safe_filename(filename: str) -> str:
    """
    Generate a safe filename by removing potentially dangerous characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    safe_filename = filename
    
    for char in dangerous_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    safe_filename = safe_filename.strip(' .')
    
    if not safe_filename:
        safe_filename = "unnamed_file"
    
    return safe_filename


def get_file_extension_from_mime_type(content_type: str) -> Optional[str]:
    """
    Get file extension from MIME type.
    Args:
        content_type: MIME type string
    Returns:
        File extension with dot (e.g., '.mp3') or None if not found
    """
    if content_type in AUDIO_MIME_TYPES:
        return AUDIO_MIME_TYPES[content_type]
    if content_type in IMAGE_MIME_TYPES:
        return IMAGE_MIME_TYPES[content_type]
    ext = mimetypes.guess_extension(content_type)
    return ext if ext else None


def validate_audio_upload(file: UploadFile, max_size: int = 100 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validate audio file upload.
    Args:
        file: FastAPI UploadFile object
        max_size: Maximum file size in bytes (default: 100MB)
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_upload_file(file, ALLOWED_AUDIO_EXTENSIONS, max_size)


def validate_image_upload(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validate image file upload.
    Args:
        file: FastAPI UploadFile object
        max_size: Maximum file size in bytes (default: 10MB)
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_upload_file(file, ALLOWED_IMAGE_EXTENSIONS, max_size)


def ensure_upload_directory(directory_path: Path) -> None:
    """
    Ensure upload directory exists.
    Args:
        directory_path: Path to the directory
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured upload directory exists: {directory_path}")
    except Exception as e:
        logger.error(f"Error creating upload directory {directory_path}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create upload directory")


def get_file_size_mb(size_bytes: int) -> float:
    """
    Convert file size from bytes to megabytes.
    Args:
        size_bytes: File size in bytes
    Returns:
        File size in megabytes
    """
    return round(size_bytes / (1024 * 1024), 2)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    Args:
        size_bytes: File size in bytes 
    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes // 1024} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{get_file_size_mb(size_bytes)} MB"
    else:
        return f"{size_bytes // (1024 * 1024 * 1024)} GB"
