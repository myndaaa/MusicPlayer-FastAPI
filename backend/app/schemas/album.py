from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for album
class AlbumBase(BaseModel):
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
    uploaded_by_user_id: int


class AlbumUpdate(BaseModel):
    title: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]] = None
    description: Optional[str] = None
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    release_date: Optional[datetime] = None
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    artist_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    band_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    class Config:
        from_attributes = True


class AlbumOut(AlbumBase):
    id: int
    uploaded_by_user_id: int

    class Config:
        from_attributes = True


# Schemas for relationships
class ArtistMinimal(BaseModel):
    id: int
    artist_stage_name: str
    artist_profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class BandMinimal(BaseModel):
    id: int
    name: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# Album song relationship schema
class AlbumSongTrack(BaseModel):
    track_number: int
    song: SongMinimal

    class Config:
        from_attributes = True


#  album output with relationships
class AlbumWithRelations(AlbumOut):
    artist: Optional[ArtistMinimal] = None
    band: Optional[BandMinimal] = None
    uploaded_by: UserMinimal
    album_songs: List[AlbumSongTrack] = []


# Album with songs list
class AlbumWithSongs(AlbumWithRelations):
    total_songs: int
    total_duration: int  # in seconds


# List schemas for pagination
class AlbumList(BaseModel):
    albums: List[AlbumOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class AlbumListWithRelations(BaseModel):
    albums: List[AlbumWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class AlbumFilter(BaseModel):
    title: Optional[str] = None
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    uploaded_by_user_id: Optional[int] = None
    release_date_from: Optional[datetime] = None
    release_date_to: Optional[datetime] = None


class AlbumSearch(BaseModel):
    query: str
    album_artist_id: Optional[int] = None
    album_band_id: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Album song management schemas
class AlbumSongAdd(BaseModel):
    song_id: int
    track_number: Annotated[int, Field(gt=0)]


class AlbumSongUpdate(BaseModel):
    track_number: Annotated[int, Field(gt=0)]


class AlbumSongRemove(BaseModel):
    song_id: int 
