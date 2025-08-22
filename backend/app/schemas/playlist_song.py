from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# Base schema for playlist-song relationship
class PlaylistSongBase(BaseModel):
    playlist_id: int
    song_id: int
    song_order: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistSongCreate(PlaylistSongBase):
    pass


class PlaylistSongUpdate(BaseModel):
    song_order: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistSongOut(PlaylistSongBase):
    id: int

    class Config:
        from_attributes = True


# Schemas for relationships
class PlaylistMinimal(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

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


# playlist_song output with relationships
class PlaylistSongWithRelations(PlaylistSongOut):
    playlist: PlaylistMinimal
    song: SongMinimal


# Playlist song list
class PlaylistSongList(BaseModel):
    playlist_id: int
    songs: List[PlaylistSongWithRelations]
    total_songs: int
    total_duration: int  # seconds


# List schemas for pagination
class PlaylistSongListPaginated(BaseModel):
    playlist_songs: List[PlaylistSongOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistSongListWithRelations(BaseModel):
    playlist_songs: List[PlaylistSongWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class PlaylistSongFilter(BaseModel):
    playlist_id: Optional[int] = None
    song_id: Optional[int] = None
    song_order: Optional[int] = None


# Playlist song management schemas
class PlaylistSongAdd(BaseModel):
    playlist_id: int
    song_id: int
    song_order: Optional[int] = None  # In case none, add to end


class PlaylistSongRemove(BaseModel):
    playlist_id: int
    song_id: int


class PlaylistSongReorder(BaseModel):
    playlist_id: int
    song_id: int
    new_song_order: int


class PlaylistSongBulkAdd(BaseModel):
    playlist_id: int
    songs: List[PlaylistSongAdd]


class PlaylistSongBulkRemove(BaseModel):
    playlist_id: int
    song_ids: List[int]


class PlaylistSongBulkReorder(BaseModel):
    playlist_id: int
    song_orders: List[dict]  # TODO HINT: [{"song_id": 1, "new_order": 3}, ...]


# Playlist song statistics
class PlaylistSongStats(BaseModel):
    playlist_id: int
    total_songs: int
    total_duration: int  # in seconds
    average_song_duration: float
    shortest_song: Optional[SongMinimal] = None
    longest_song: Optional[SongMinimal] = None
    most_common_artist: Optional[str] = None
    most_common_genre: Optional[str] = None


# Playlist song validation schema
class PlaylistSongValidation(BaseModel):
    playlist_id: int
    song_id: int

    @model_validator(mode="after")
    def validate_unique_song(self) -> "PlaylistSongValidation":
        """Ensure song is not already in playlist"""
        # TODO:  validation would be done in the service layer
        return self


# Playlist song search
class PlaylistSongSearch(BaseModel):
    playlist_id: int
    query: str  # Search in song title, artist, or band name
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Playlist song export
class PlaylistSongExport(BaseModel):
    playlist_id: int
    format: str = "json"  # json, csv, m3u, etc.
    include_song_details: bool = True
    include_metadata: bool = True


# Playlist song recommendations
class PlaylistSongRecommendation(BaseModel):
    playlist_id: int
    recommended_songs: List[SongMinimal]
    recommendation_reason: str  # Response to frontend:  "Based on playlist genre", "Similar to existing songs"
    confidence_score: float  # 0.0 to 1.0 
