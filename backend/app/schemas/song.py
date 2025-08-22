from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for song
class SongBase(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    genre_id: int
    band_id: Optional[int] = None
    artist_id: Optional[int] = None
    release_date: datetime
    song_duration: Annotated[int, Field(gt=0)]  # Duration in seconds, positive
    file_path: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    artist_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    band_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    @model_validator(mode="after")
    def validate_artist_or_band(self) -> "SongBase":
        """Ensure either artist_id or band_id is provided, but not both"""
        if self.artist_id is not None and self.band_id is not None:
            raise ValueError("Song cannot have both artist_id and band_id")
        if self.artist_id is None and self.band_id is None:
            raise ValueError("Song must have either artist_id or band_id")
        return self

    class Config:
        from_attributes = True


class SongCreate(SongBase):
    uploaded_by_user_id: int


class SongUpdate(BaseModel):
    title: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]] = None
    genre_id: Optional[int] = None
    band_id: Optional[int] = None
    artist_id: Optional[int] = None
    release_date: Optional[datetime] = None
    song_duration: Optional[Annotated[int, Field(gt=0)]] = None
    file_path: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]] = None
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    artist_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    band_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    class Config:
        from_attributes = True


class SongOut(SongBase):
    id: int
    uploaded_by_user_id: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schema for relationships
class GenreMinimal(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


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


# song output with relationships
class SongWithRelations(SongOut):
    genre: GenreMinimal
    artist: Optional[ArtistMinimal] = None
    band: Optional[BandMinimal] = None
    uploaded_by: UserMinimal


# Song status update
class SongStatus(BaseModel):
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# List schemas for pagination
class SongList(BaseModel):
    songs: List[SongOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class SongListWithRelations(BaseModel):
    songs: List[SongWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class SongFilter(BaseModel):
    title: Optional[str] = None
    genre_id: Optional[int] = None
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    is_disabled: Optional[bool] = None
    uploaded_by_user_id: Optional[int] = None


class SongSearch(BaseModel):
    query: str
    genre_id: Optional[int] = None
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0) 
