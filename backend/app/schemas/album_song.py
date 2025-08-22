from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# Base schema for album-song relationship
class AlbumSongBase(BaseModel):
    album_id: int
    song_id: int
    track_number: Annotated[int, Field(gt=0)]

    class Config:
        from_attributes = True


class AlbumSongCreate(AlbumSongBase):
    pass


class AlbumSongUpdate(BaseModel):
    track_number: Annotated[int, Field(gt=0)]

    class Config:
        from_attributes = True


class AlbumSongOut(AlbumSongBase):
    id: int

    class Config:
        from_attributes = True


# Nested schemas for relationships
class AlbumMinimal(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = None
    release_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class SongMinimal(BaseModel):
    id: int
    title: str
    song_duration: int
    cover_image: Optional[str] = None
    artist_name: Optional[str] = None
    band_name: Optional[str] = None

    class Config:
        from_attributes = True


# album-song output with relationships
class AlbumSongWithRelations(AlbumSongOut):
    album: AlbumMinimal
    song: SongMinimal


# Album track list
class AlbumTrackList(BaseModel):
    album_id: int
    tracks: List[AlbumSongWithRelations]
    total_tracks: int
    total_duration: int  # in seconds


# List schemas for pagination
class AlbumSongList(BaseModel):
    album_songs: List[AlbumSongOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AlbumSongListWithRelations(BaseModel):
    album_songs: List[AlbumSongWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class AlbumSongFilter(BaseModel):
    album_id: Optional[int] = None
    song_id: Optional[int] = None
    track_number: Optional[int] = None


# Album song management schemas
class AlbumSongAdd(BaseModel):
    album_id: int
    song_id: int
    track_number: Annotated[int, Field(gt=0)]


class AlbumSongRemove(BaseModel):
    album_id: int
    song_id: int


class AlbumSongReorder(BaseModel):
    album_id: int
    song_id: int
    new_track_number: Annotated[int, Field(gt=0)]


class AlbumSongBulkAdd(BaseModel):
    album_id: int
    songs: List[AlbumSongAdd]


class AlbumSongBulkRemove(BaseModel):
    album_id: int
    song_ids: List[int]


# Album song statistics
class AlbumSongStats(BaseModel):
    album_id: int
    total_tracks: int
    total_duration: int  # in seconds
    average_track_duration: float
    shortest_track: Optional[SongMinimal] = None
    longest_track: Optional[SongMinimal] = None


# track validation schema
class TrackNumberValidation(BaseModel):
    album_id: int
    track_number: int

    @model_validator(mode="after")
    def validate_track_number(self) -> "TrackNumberValidation":
        """Ensure track number is positive"""
        if self.track_number <= 0:
            raise ValueError("Track number must be positive")
        return self 
