from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints, Field, model_validator


# Base schema for band
class BandBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    bio: Optional[str] = None
    profile_picture: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    social_link: Optional[dict] = None  # JSON field for social media links

    class Config:
        from_attributes = True


class BandCreate(BandBase):
    pass


class BandUpdate(BaseModel):
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


class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

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


# Band with statistics
class BandWithStats(BandWithRelations):
    total_songs: int
    total_albums: int
    total_members: int
    current_members: int
    total_followers: int


# Band status update
class BandStatus(BaseModel):
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# List schemas for pagination
class BandList(BaseModel):
    bands: List[BandOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class BandListWithRelations(BaseModel):
    bands: List[BandWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class BandFilter(BaseModel):
    name: Optional[str] = None
    is_disabled: Optional[bool] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    has_members: Optional[bool] = None
    has_songs: Optional[bool] = None


class BandSearch(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Band following schema
class BandFollow(BaseModel):
    band_id: int
    user_id: int


class BandUnfollow(BaseModel):
    band_id: int
    user_id: int


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


# Band member management schemas
class BandMemberAdd(BaseModel):
    band_id: int
    artist_id: int
    joined_on: Optional[datetime] = None


class BandMemberRemove(BaseModel):
    band_id: int
    artist_id: int
    left_at: Optional[datetime] = None


class BandMemberBulkAdd(BaseModel):
    band_id: int
    artists: List[BandMemberAdd]


class BandMemberBulkRemove(BaseModel):
    band_id: int
    artist_ids: List[int]


# Band statistics
class BandStats(BaseModel):
    total_bands: int
    active_bands: int
    bands_with_members: int
    bands_with_songs: int
    bands_with_albums: int
    average_members_per_band: float
    most_popular_band: Optional[BandOut] = None


# Band recommendations
class BandRecommendation(BaseModel):
    user_id: int
    recommended_bands: List[BandOut]
    recommendation_reason: str  
    confidence_score: float  # 0.0 to 1.0 
