from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for artist
class ArtistBase(BaseModel):
    artist_stage_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    artist_bio: Optional[str] = None
    artist_profile_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    artist_social_link: Optional[dict] = None  # JSON field for social media links

    class Config:
        from_attributes = True


class ArtistCreate(ArtistBase):
    linked_user_account: int


class ArtistUpdate(BaseModel):
    artist_stage_name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]] = None
    artist_bio: Optional[str] = None
    artist_profile_image: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    artist_social_link: Optional[dict] = None

    class Config:
        from_attributes = True


class ArtistOut(ArtistBase):
    id: int
    linked_user_account: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schemas for relationships
class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

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


class BandMinimal(BaseModel):
    id: int
    name: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


# Band membership schema
class ArtistBandMembership(BaseModel):
    band_member_id: int
    band: BandMinimal
    joined_on: datetime
    left_at: Optional[datetime] = None
    is_current_member: bool

    class Config:
        from_attributes = True


# artist output with relationships
class ArtistWithRelations(ArtistOut):
    linked_user: UserMinimal
    songs: List[SongMinimal] = []
    albums: List[AlbumMinimal] = []
    band_memberships: List[ArtistBandMembership] = []


# Artist with statistics
class ArtistWithStats(ArtistWithRelations):
    total_songs: int
    total_albums: int
    total_followers: int
    total_bands: int


# Artist status update
class ArtistStatus(BaseModel):
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# List schemas for pagination
class ArtistList(BaseModel):
    artists: List[ArtistOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class ArtistListWithRelations(BaseModel):
    artists: List[ArtistWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class ArtistFilter(BaseModel):
    artist_stage_name: Optional[str] = None
    linked_user_account: Optional[int] = None
    is_disabled: Optional[bool] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None


class ArtistSearch(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Artist following schema
class ArtistFollow(BaseModel):
    artist_id: int
    user_id: int


class ArtistUnfollow(BaseModel):
    artist_id: int
    user_id: int


# Artist social links schema
class ArtistSocialLinks(BaseModel):
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None
    youtube: Optional[str] = None
    spotify: Optional[str] = None
    website: Optional[str] = None

    @model_validator(mode="after")
    def validate_at_least_one_link(self) -> "ArtistSocialLinks":
        """Ensure at least one social link is provided"""
        if not any([self.facebook, self.twitter, self.instagram, self.youtube, self.spotify, self.website]):
            raise ValueError("At least one social link must be provided")
        return self 
