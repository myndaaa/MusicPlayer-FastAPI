"""
File service for handling uploads, validation, and file management.
Handles audio files, images, and metadata extraction.
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import aiofiles
from mutagen import File as MutagenFile
from PIL import Image
import logging

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg': '.mp3',
    'audio/wav': '.wav', 
    'audio/flac': '.flac',
    'audio/x-flac': '.flac'
}

ALLOWED_IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp'
}

MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB

UPLOAD_BASE = Path("uploads")
SONGS_DIR = UPLOAD_BASE / "songs"
COVERS_DIR = UPLOAD_BASE / "covers"
PROFILES_DIR = UPLOAD_BASE / "profiles"
ALBUMS_DIR = UPLOAD_BASE / "albums"
TEMP_DIR = UPLOAD_BASE / "temp"


class FileService:
    """Service for handling file uploads, validation, and management."""
    
    def __init__(self):
        """Initialize file service and ensure directories exist."""
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create upload directories if they don't exist."""
        directories = [SONGS_DIR, COVERS_DIR, PROFILES_DIR, ALBUMS_DIR, TEMP_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    def validate_audio_file(self, file_path: Path, content_type: str) -> Tuple[bool, str]:
        """
        Validate audio file type and size.
        
        Args:
            file_path: Path to the audio file
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, "File not found"
        
        try:
            if file_path.stat().st_size > MAX_AUDIO_SIZE:
                return False, f"File too large. Maximum size is {MAX_AUDIO_SIZE // (1024*1024)}MB"
            
            if content_type not in ALLOWED_AUDIO_TYPES:
                return False, f"Unsupported audio format. Allowed: {', '.join(ALLOWED_AUDIO_TYPES.keys())}"
            
            expected_ext = ALLOWED_AUDIO_TYPES[content_type]
            if file_path.suffix.lower() != expected_ext:
                return False, f"File extension doesn't match content type. Expected: {expected_ext}"
            
            return True, ""
        except OSError as e:
            return False, f"Error accessing file: {str(e)}"
    
    def validate_image_file(self, file_path: Path, content_type: str) -> Tuple[bool, str]:
        """
        Validate image file type and size.
        
        Args:
            file_path: Path to the image file
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, "File not found"
        
        try:
            if file_path.stat().st_size > MAX_IMAGE_SIZE:
                return False, f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024*1024)}MB"
            
            if content_type not in ALLOWED_IMAGE_TYPES:
                return False, f"Unsupported image format. Allowed: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
            
            expected_ext = ALLOWED_IMAGE_TYPES[content_type]
            if file_path.suffix.lower() != expected_ext:
                return False, f"File extension doesn't match content type. Expected: {expected_ext}"
            
            return True, ""
        except OSError as e:
            return False, f"Error accessing file: {str(e)}"
    
    def generate_unique_filename(self, original_filename: str, file_id: int, file_type: str) -> str:
        """
        Generate a unique filename to avoid conflicts.
        
        Args:
            original_filename: Original uploaded filename
            file_id: Database ID of the file (song_id, album_id, etc.)
            file_type: Type of file (song, cover, profile, album)
            
        Returns:
            Unique filename
        """
        ext = Path(original_filename).suffix.lower()
        
        unique_id = str(uuid.uuid4())[:8]
        
        return f"{file_type}_{file_id}_{unique_id}{ext}"
    
    def get_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return {"duration": 0, "bitrate": 0}
            
            audio = MutagenFile(str(file_path))
            
            if audio is None:
                return {"duration": 0, "bitrate": 0}
            
            metadata = {
                "duration": int(audio.info.length) if hasattr(audio.info, 'length') else 0,
                "bitrate": audio.info.bitrate if hasattr(audio.info, 'bitrate') else 0,
                "sample_rate": audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else 0,
                "channels": audio.info.channels if hasattr(audio.info, 'channels') else 0
            }
            
            if hasattr(audio, 'tags'):
                tags = audio.tags
                if tags:
                    metadata.update({
                        "title": str(tags.get('title', [''])[0]) if 'title' in tags else None,
                        "artist": str(tags.get('artist', [''])[0]) if 'artist' in tags else None,
                        "album": str(tags.get('album', [''])[0]) if 'album' in tags else None,
                        "genre": str(tags.get('genre', [''])[0]) if 'genre' in tags else None,
                        "year": str(tags.get('date', [''])[0]) if 'date' in tags else None
                    })
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting audio metadata from {file_path}: {e}")
            return {"duration": 0, "bitrate": 0}
    
    def get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from image file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            with Image.open(file_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_bytes": file_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Error extracting image metadata from {file_path}: {e}")
            return {"width": 0, "height": 0, "format": None, "mode": None, "size_bytes": 0}
    
    async def save_uploaded_file(self, temp_path: Path, destination_path: Path) -> bool:
        """
        Save uploaded file from temporary location to final destination.
        
        Args:
            temp_path: Temporary file path
            destination_path: Final destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(temp_path, destination_path)
            
            
            logger.info(f"File saved successfully: {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file from {temp_path} to {destination_path}: {e}")
            return False
    
    def get_file_path(self, file_type: str, filename: str) -> Path:
        """
        Get the full path for a file based on its type.
        
        Args:
            file_type: Type of file (song, cover, profile, album)
            filename: Name of the file
            
        Returns:
            Full path to the file
        """
        type_to_dir = {
            "song": SONGS_DIR,
            "cover": COVERS_DIR,
            "profile": PROFILES_DIR,
            "album": ALBUMS_DIR
        }
        
        directory = type_to_dir.get(file_type, TEMP_DIR)
        return directory / filename
    
    def file_exists(self, file_type: str, filename: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_type: Type of file (song, cover, profile, album)
            filename: Name of the file
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.get_file_path(file_type, filename)
        return file_path.exists()
    
    def delete_file(self, file_type: str, filename: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_type: Type of file (song, cover, profile, album)
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.get_file_path(file_type, filename)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    def get_file_size(self, file_type: str, filename: str) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_type: Type of file (song, cover, profile, album)
            filename: Name of the file
            
        Returns:
            File size in bytes
        """
        file_path = self.get_file_path(file_type, filename)
        return file_path.stat().st_size if file_path.exists() else 0
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            current_time = datetime.now()
            
            for temp_file in TEMP_DIR.glob("*"):
                if temp_file.is_file():
                    file_age = current_time - datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_age.total_seconds() > max_age_hours * 3600:
                        temp_file.unlink()
                        cleaned_count += 1
                        logger.info(f"Cleaned up temp file: {temp_file}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
            return 0


file_service = FileService()
