"""
Clean Album schemas without redundancy.
"""

from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


class AlbumBase(BaseModel):
    """Base schema for album data with common fields"""
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    description: Optional[str] = None
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    release_date: Optional[datetime] = None
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    artist_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    band_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    @model_validator(mode="after")
    def validate_artist_or_band(self) -> "AlbumBase":
        """Ensure either album_artist_id or album_band_id is provided, but not both"""
        if self.album_artist_id is not None and self.album_band_id is not None:
            raise ValueError("Album cannot have both album_artist_id and album_band_id")
        return self

    class Config:
        from_attributes = True


class AlbumCreate(AlbumBase):
    """Schema for creating a new album"""
    pass


class AlbumUpdate(BaseModel):
    """Schema for updating album metadata"""
    title: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]] = None
    description: Optional[str] = None
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    release_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlbumOut(AlbumBase):
    """Schema for album output with all fields"""
    id: int
    uploaded_by_user_id: int

    class Config:
        from_attributes = True


# Minimal schemas for relationships (reused across modules)
class ArtistMinimal(BaseModel):
    """Minimal artist schema for relationships"""
    id: int
    artist_stage_name: str
    artist_profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class BandMinimal(BaseModel):
    """Minimal band schema for relationships"""
    id: int
    name: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


class UserMinimal(BaseModel):
    """Minimal user schema for relationships"""
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class SongMinimal(BaseModel):
    """Minimal song schema for relationships"""
    id: int
    title: str
    song_duration: int
    cover_image: Optional[str] = None
    artist_name: Optional[str] = None
    band_name: Optional[str] = None

    class Config:
        from_attributes = True


class AlbumWithRelations(AlbumOut):
    """Schema for album output with relationships"""
    artist: Optional[ArtistMinimal] = None
    band: Optional[BandMinimal] = None
    uploaded_by: UserMinimal


class AlbumWithSongs(AlbumWithRelations):
    """Schema for album with songs list"""
    total_songs: int
    total_duration: int  # in seconds


# List schemas for pagination
class AlbumList(BaseModel):
    """Schema for paginated album list"""
    albums: List[AlbumOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AlbumListWithRelations(BaseModel):
    """Schema for paginated album list with relationships"""
    albums: List[AlbumWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class AlbumFilter(BaseModel):
    """Schema for album filtering"""
    title: Optional[str] = None
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    uploaded_by_user_id: Optional[int] = None
    release_date_from: Optional[datetime] = None
    release_date_to: Optional[datetime] = None


class AlbumSearch(BaseModel):
    """Schema for album search"""
    query: str
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AlbumStats(BaseModel):
    """Schema for album statistics"""
    total_albums: int
    albums_by_artist: int
    albums_by_band: int
    most_uploaded_artist: Optional[str] = None
    most_uploaded_band: Optional[str] = None 
