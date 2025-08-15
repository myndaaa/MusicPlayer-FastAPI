"""
Clean AlbumSong schemas without redundancy.
"""

from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class AlbumSongBase(BaseModel):
    """Base schema for album-song relationship data"""
    album_id: int
    song_id: int
    track_number: Annotated[int, Field(gt=0)]

    class Config:
        from_attributes = True


class AlbumSongCreate(AlbumSongBase):
    """Schema for creating album-song relationship"""
    pass


class AlbumSongUpdate(BaseModel):
    """Schema for updating album-song relationship"""
    track_number: Annotated[int, Field(gt=0)]

    class Config:
        from_attributes = True


class AlbumSongOut(AlbumSongBase):
    """Schema for album-song output with all fields"""
    id: int

    class Config:
        from_attributes = True


# Minimal schemas for relationships (reused from album.py)
class AlbumMinimal(BaseModel):
    """Minimal album schema for relationships"""
    id: int
    title: str
    cover_image: Optional[str] = None
    release_date: Optional[datetime] = None

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


class AlbumSongWithRelations(AlbumSongOut):
    """Schema for album-song output with relationships"""
    album: AlbumMinimal
    song: SongMinimal


# List schemas for pagination
class AlbumSongList(BaseModel):
    """Schema for paginated album-song list"""
    album_songs: List[AlbumSongOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AlbumSongListWithRelations(BaseModel):
    """Schema for paginated album-song list with relationships"""
    album_songs: List[AlbumSongWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Album song management schemas
class AlbumSongAdd(BaseModel):
    """Schema for adding song to album"""
    song_id: int
    track_number: Annotated[int, Field(gt=0)]


class AlbumSongBulkAdd(BaseModel):
    """Schema for bulk adding songs to album"""
    songs: List[AlbumSongAdd]


class AlbumSongBulkReorder(BaseModel):
    """Schema for bulk reordering album songs"""
    tracks: List[AlbumSongAdd]  # List of song_id and new track_number


class AlbumSongStats(BaseModel):
    """Schema for album song statistics"""
    album_id: int
    total_tracks: int
    total_duration: int  # in seconds
    average_track_duration: float
    shortest_track: Optional[SongMinimal] = None
    longest_track: Optional[SongMinimal] = None 
