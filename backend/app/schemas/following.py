from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# Base schema for following
class FollowingBase(BaseModel):
    user_id: int
    artist_id: Optional[int] = None
    band_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_following_target(self) -> "FollowingBase":
        """Ensure either artist_id or band_id is provided, but not both"""
        if self.artist_id is not None and self.band_id is not None:
            raise ValueError("Cannot follow both artist and band simultaneously")
        if self.artist_id is None and self.band_id is None:
            raise ValueError("Must follow either an artist or a band")
        return self

    class Config:
        from_attributes = True


class FollowingCreate(FollowingBase):
    pass


class FollowingUpdate(BaseModel):
    started_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FollowingOut(FollowingBase):
    id: int
    started_at: datetime

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


# Following output with relationships
class FollowingWithRelations(FollowingOut):
    user: UserMinimal
    artist: Optional[ArtistMinimal] = None
    band: Optional[BandMinimal] = None


# User following list
class UserFollowingList(BaseModel):
    user_id: int
    following: List[FollowingWithRelations]
    following_artists: List[ArtistMinimal]
    following_bands: List[BandMinimal]
    total_following: int
    artist_count: int
    band_count: int


# Artist followers list
class ArtistFollowersList(BaseModel):
    artist_id: int
    followers: List[UserMinimal]
    total_followers: int


# Band followers list
class BandFollowersList(BaseModel):
    band_id: int
    followers: List[UserMinimal]
    total_followers: int


# List schemas for pagination
class FollowingList(BaseModel):
    followings: List[FollowingOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class FollowingListWithRelations(BaseModel):
    followings: List[FollowingWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class FollowingFilter(BaseModel):
    user_id: Optional[int] = None
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    started_at_from: Optional[datetime] = None
    started_at_to: Optional[datetime] = None


class FollowingSearch(BaseModel):
    user_id: int
    query: Optional[str] = None  # Search in artist/band names
    follow_type: Optional[str] = None  # "artist", "band", or None for both
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Following management schemas
class FollowingAdd(BaseModel):
    user_id: int
    artist_id: Optional[int] = None
    band_id: Optional[int] = None


class FollowingRemove(BaseModel):
    user_id: int
    artist_id: Optional[int] = None
    band_id: Optional[int] = None


class FollowingToggle(BaseModel):
    user_id: int
    artist_id: Optional[int] = None
    band_id: Optional[int] = None


# Following statistics
class FollowingStats(BaseModel):
    total_followings: int
    unique_users: int
    unique_artists: int
    unique_bands: int
    most_followed_artist: Optional[ArtistMinimal] = None
    most_followed_band: Optional[BandMinimal] = None
    most_active_follower: Optional[UserMinimal] = None


# User following statistics
class UserFollowingStats(BaseModel):
    user_id: int
    total_following: int
    artist_count: int
    band_count: int
    following_since: Optional[datetime] = None
    most_recent_follow: Optional[datetime] = None


# Artist/Band following statistics
class ArtistBandFollowingStats(BaseModel):
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    total_followers: int
    followers_growth_rate: float  # followers per day
    top_followers: List[UserMinimal]  # most active followers


# Following recommendations
class FollowingRecommendation(BaseModel):
    user_id: int
    recommended_artists: List[ArtistMinimal]
    recommended_bands: List[BandMinimal]
    recommendation_reason: str  # e.g., "Based on your listening history", "Popular among similar users"
    confidence_score: float  # 0.0 to 1.0


# Following activity
class FollowingActivity(BaseModel):
    user_id: int
    activities: List[dict]  # Timeline of following activities
    # [{"date": "2024-01-01", "action": "followed", "target": {...}}, ...]


# Following export
class FollowingExport(BaseModel):
    user_id: Optional[int] = None
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    format: str = "json"  # json, csv, etc.
    include_details: bool = True


# Following notifications
class FollowingNotification(BaseModel):
    user_id: int
    target_id: int  # artist_id or band_id
    target_type: str  # "artist" or "band"
    notification_type: str  # "new_release", "new_song", "new_album", etc.
    message: str
    timestamp: datetime 
