from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for playlist
class PlaylistBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    description: Optional[Annotated[str, StringConstraints(max_length=255)]] = None

    class Config:
        from_attributes = True


class PlaylistCreate(PlaylistBase):
    owner_id: int


class PlaylistUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = None
    description: Optional[Annotated[str, StringConstraints(max_length=255)]] = None

    class Config:
        from_attributes = True


class PlaylistOut(PlaylistBase):
    id: int
    owner_id: int
    created_at: datetime

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


# Playlist song relationship schema
class PlaylistSongTrack(BaseModel):
    song_order: Optional[int] = None
    song: SongMinimal

    class Config:
        from_attributes = True


# Playlist collaborator schema
class PlaylistCollaborator(BaseModel):
    id: int
    collaborator: UserMinimal
    can_edit: bool
    added_at: datetime
    added_by: Optional[UserMinimal] = None

    class Config:
        from_attributes = True


# playlist output with relationships
class PlaylistWithRelations(PlaylistOut):
    owner: UserMinimal
    playlist_songs: List[PlaylistSongTrack] = []
    playlist_collaborators: List[PlaylistCollaborator] = []


# Playlist with songs list
class PlaylistWithSongs(PlaylistWithRelations):
    total_songs: int
    total_duration: int  # in seconds


# List schemas for pagination
class PlaylistList(BaseModel):
    playlists: List[PlaylistOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistListWithRelations(BaseModel):
    playlists: List[PlaylistWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class PlaylistFilter(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None
    collaborator_id: Optional[int] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None


class PlaylistSearch(BaseModel):
    query: str
    owner_id: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Playlist song management schemas
class PlaylistSongAdd(BaseModel):
    song_id: int
    song_order: Optional[int] = None


class PlaylistSongUpdate(BaseModel):
    song_order: int


class PlaylistSongRemove(BaseModel):
    song_id: int


# Playlist collaborator management schemas
class PlaylistCollaboratorAdd(BaseModel):
    collaborator_id: int
    can_edit: bool = False


class PlaylistCollaboratorUpdate(BaseModel):
    can_edit: bool


class PlaylistCollaboratorRemove(BaseModel):
    collaborator_id: int


# Playlist sharing schemas
class PlaylistShare(BaseModel):
    playlist_id: int
    user_ids: List[int] 
    can_edit: bool = False


# Playlist statistics
class PlaylistStats(BaseModel):
    total_songs: int
    total_duration: int  # in seconds
    total_collaborators: int
    created_at: datetime
    last_modified: datetime 
