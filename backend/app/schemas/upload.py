"""
Schemas for file upload and metadata responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response schema for successful file upload."""
    
    success: bool = Field(description="Upload success status")
    filename: str = Field(description="Generated unique filename")
    original_filename: str = Field(description="Original uploaded filename")
    file_size: int = Field(description="File size in bytes")
    file_size_mb: float = Field(description="File size in megabytes")
    content_type: str = Field(description="MIME type of the file")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Extracted file metadata")


class AudioUploadResponse(FileUploadResponse):
    """Response schema for audio file upload."""
    
    duration: Optional[int] = Field(default=None, description="Audio duration in seconds")
    bitrate: Optional[int] = Field(default=None, description="Audio bitrate")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate")
    channels: Optional[int] = Field(default=None, description="Number of audio channels")


class ImageUploadResponse(FileUploadResponse):
    """Response schema for image file upload."""
    
    width: Optional[int] = Field(default=None, description="Image width in pixels")
    height: Optional[int] = Field(default=None, description="Image height in pixels")
    format: Optional[str] = Field(default=None, description="Image format")


class FileMetadata(BaseModel):
    """Schema for file metadata."""
    
    filename: str = Field(description="File filename")
    file_size: int = Field(description="File size in bytes")
    content_type: str = Field(description="MIME type")
    created_at: datetime = Field(description="File creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class UploadError(BaseModel):
    """Schema for upload error responses."""
    
    error: str = Field(description="Error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
    field: Optional[str] = Field(default=None, description="Field that caused the error")


class FileInfo(BaseModel):
    """Schema for file information."""
    
    id: int = Field(description="File ID")
    filename: str = Field(description="File filename")
    file_path: str = Field(description="File path")
    file_size: int = Field(description="File size in bytes")
    content_type: str = Field(description="MIME type")
    created_at: datetime = Field(description="File creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="File last update timestamp")
    is_public: bool = Field(description="Whether file is publicly accessible")
    access_url: Optional[str] = Field(default=None, description="Public access URL")
