from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field


# Base schema for history
class HistoryBase(BaseModel):
    user_id: int
    song_id: int

    class Config:
        from_attributes = True


class HistoryCreate(HistoryBase):
    pass


class HistoryUpdate(BaseModel):
    played_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HistoryOut(HistoryBase):
    id: int
    played_at: datetime

    class Config:
        from_attributes = True


# Schemas for relationships
class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

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


# History output with relationships
class HistoryWithRelations(HistoryOut):
    user: UserMinimal
    song: SongMinimal


# History with song details
class HistoryWithSongDetails(HistoryWithRelations):
    song_genre: Optional[str] = None
    song_album: Optional[str] = None


# List schemas for pagination
class HistoryList(BaseModel):
    history: List[HistoryOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class HistoryListWithRelations(BaseModel):
    history: List[HistoryWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class HistoryFilter(BaseModel):
    user_id: Optional[int] = None
    song_id: Optional[int] = None
    played_at_from: Optional[datetime] = None
    played_at_to: Optional[datetime] = None


class HistorySearch(BaseModel):
    user_id: int
    query: Optional[str] = None  # Search in song title, artist, or band name
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# History management schemas
class HistoryAdd(BaseModel):
    user_id: int
    song_id: int


class HistoryRemove(BaseModel):
    user_id: int
    song_id: int


class HistoryClear(BaseModel):
    user_id: int


# History statistics
class HistoryStats(BaseModel):
    total_listens: int
    unique_songs: int
    total_duration: int  # in seconds
    most_listened_song: Optional[SongMinimal] = None
    most_listened_artist: Optional[str] = None
    most_listened_genre: Optional[str] = None
    listening_streak: int  # consecutive days
    last_listened: Optional[datetime] = None


# User listening history
class UserListeningHistory(BaseModel):
    user_id: int
    recent_listens: List[HistoryWithRelations]
    top_songs: List[SongMinimal]
    top_artists: List[str]
    top_genres: List[str]
    listening_stats: HistoryStats


# History export schema
class HistoryExport(BaseModel):
    user_id: int
    format: str = "json"  
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_song_details: bool = True 
