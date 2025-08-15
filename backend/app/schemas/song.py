from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


class SongBase(BaseModel):
    """Base schema for song data with common fields"""
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


class SongUploadByArtist(SongBase):
    """Schema for artist uploading their own song"""
    pass


class SongUploadByBand(SongBase):
    """Schema for band member uploading band song"""
    pass


class SongUploadByAdmin(SongBase):
    """Schema for admin uploading for any artist/band (including dead artists)"""
    artist_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    band_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    @model_validator(mode="after")
    def validate_admin_upload(self) -> "SongUploadByAdmin":
        """For admin uploads, either artist_name or band_name must be provided if no IDs"""
        if self.artist_id is None and self.band_id is None:
            if not self.artist_name and not self.band_name:
                raise ValueError("Admin upload must specify either artist_name or band_name when no IDs provided")
        return self


class SongUpdate(BaseModel):
    """Schema for updating song metadata"""
    title: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]] = None
    genre_id: Optional[int] = None
    release_date: Optional[datetime] = None
    song_duration: Optional[Annotated[int, Field(gt=0)]] = None
    cover_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None

    class Config:
        from_attributes = True


class SongOut(SongBase):
    """Schema for song output with all fields"""
    id: int
    uploaded_by_user_id: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SongWithRelations(SongOut):
    """Schema for song output with relationships"""
    genre: "GenreMinimal"
    artist: Optional["ArtistMinimal"] = None
    band: Optional["BandMinimal"] = None
    uploaded_by: "UserMinimal"

    class Config:
        from_attributes = True


class GenreMinimal(BaseModel):
    """Minimal genre schema for relationships"""
    id: int
    name: str

    class Config:
        from_attributes = True


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


class SongStats(BaseModel):
    """Schema for song statistics"""
    total_songs: int
    active_songs: int
    disabled_songs: int
    songs_by_artist: int
    songs_by_band: int
    most_uploaded_artist: Optional[str] = None
    most_uploaded_band: Optional[str] = None

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
