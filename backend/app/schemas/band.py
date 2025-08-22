from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for band - reused by most schemas
class BandBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    bio: Optional[str] = None
    profile_picture: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    social_link: Optional[dict] = None

    class Config:
        from_attributes = True


class BandCreate(BandBase):
    pass


class BandUpdate(BandBase):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]] = None
    bio: Optional[str] = None
    profile_picture: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    social_link: Optional[dict] = None

    class Config:
        from_attributes = True


class BandOut(BandBase):
    id: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Nested schemas for relationships
class ArtistMinimal(BaseModel):
    id: int
    artist_stage_name: str
    artist_profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class SongMinimal(BaseModel):
    id: int
    title: str
    song_duration: int
    cover_image: Optional[str] = None
    release_date: datetime

    class Config:
        from_attributes = True


class AlbumMinimal(BaseModel):
    id: int
    title: str
    cover_image: Optional[str] = None
    release_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Band member schema
class BandMember(BaseModel):
    band_member_id: int
    artist: ArtistMinimal
    joined_on: datetime
    left_at: Optional[datetime] = None
    is_current_member: bool

    class Config:
        from_attributes = True


# Comprehensive band output with relationships
class BandWithRelations(BandOut):
    songs: List[SongMinimal] = []
    albums: List[AlbumMinimal] = []
    members: List[BandMember] = []


# Band statistics
class BandStats(BaseModel):
    total_bands: int
    active_bands: int
    disabled_bands: int
    bands_with_songs: int
    bands_with_albums: int

    class Config:
        from_attributes = True


# Search and filter schemas
class BandSearch(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Band member management schemas
class BandMemberAdd(BaseModel):
    band_id: int
    artist_id: int
    joined_on: Optional[datetime] = None


class BandMemberRemove(BaseModel):
    band_id: int
    artist_id: int
    left_at: Optional[datetime] = None


# Band social links schema
class BandSocialLinks(BaseModel):
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    spotify: Optional[str] = None
    website: Optional[str] = None

    @model_validator(mode="after")
    def validate_at_least_one_link(self) -> "BandSocialLinks":
        """Ensure at least one social link is provided"""
        if not any([self.facebook, self.twitter, self.instagram, self.youtube, self.spotify, self.website]):
            raise ValueError("At least one social link must be provided")
        return self 
