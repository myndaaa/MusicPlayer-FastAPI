"""
Schemas for combined song creation and file upload operations.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class SongCreateWithUpload(BaseModel):
    """Schema for creating a song with file upload in one operation."""
    
    title: str = Field(..., min_length=1, max_length=150, description="Song title")
    genre_id: int = Field(..., description="Genre ID")
    band_id: Optional[int] = Field(None, description="Band ID (optional if artist_id provided)")
    artist_id: Optional[int] = Field(None, description="Artist ID (optional if band_id provided)")
    release_date: str = Field(..., description="Song release date")
    song_duration: int = Field(0, description="Audio duration in seconds")
    file_path: str = Field("", description="File path (set after upload)")
    cover_image: Optional[str] = Field(None, description="Cover image path")
    artist_name: Optional[str] = Field(None, max_length=100, description="Artist name (for admin uploads)")
    band_name: Optional[str] = Field(None, max_length=100, description="Band name (for admin uploads)")
    
    @model_validator(mode="after")
    def validate_artist_or_band(self) -> "SongCreateWithUpload":
        """Ensure either artist_id or band_id is provided, but not both"""
        if self.artist_id is not None and self.band_id is not None:
            raise ValueError("Song cannot have both artist_id and band_id")
        if self.artist_id is None and self.band_id is None:
            raise ValueError("Song must have either artist_id or band_id")
        return self


class SongCreateWithUploadByArtist(SongCreateWithUpload):
    """Schema for artist uploading their own song."""
    artist_id: int = Field(..., description="Artist ID (required for artist uploads)")
    band_id: Optional[int] = Field(None, description="Band ID (not used for artist uploads)")


class SongCreateWithUploadByBand(SongCreateWithUpload):
    """Schema for band member uploading band song."""
    band_id: int = Field(..., description="Band ID (required for band uploads)")
    artist_id: Optional[int] = Field(None, description="Artist ID (not used for band uploads)")


class SongCreateWithUploadByAdmin(SongCreateWithUpload):
    """Schema for admin uploading for any artist/band."""
    
    @model_validator(mode="after")
    def validate_admin_upload(self) -> "SongCreateWithUploadByAdmin":
        """For admin uploads, either artist_name or band_name must be provided if no IDs"""
        if self.artist_id is None and self.band_id is None:
            if not self.artist_name and not self.band_name:
                raise ValueError("Admin upload must specify either artist_name or band_name when no IDs provided")
        return self


class SongUploadResponse(BaseModel):
    """Response schema for successful song creation with upload."""
    
    song_id: int = Field(description="Created song ID")
    title: str = Field(description="Song title")
    filename: str = Field(description="Generated unique filename")
    stream_url: str = Field(description="URL to stream the song")
    duration: int = Field(description="Audio duration in seconds")
    file_size: int = Field(description="File size in bytes")
    message: str = Field(description="Success message")


class CoverUploadRequest(BaseModel):
    """Schema for uploading cover image for existing song."""
    
    song_id: int = Field(..., description="ID of the song to add cover to")


class CoverUploadResponse(BaseModel):
    """Response schema for successful cover upload."""
    
    song_id: int = Field(description="Song ID")
    title: str = Field(description="Song title")
    cover_filename: str = Field(description="Generated unique filename")
    cover_url: str = Field(description="URL to view the cover image")
    message: str = Field(description="Success message")
