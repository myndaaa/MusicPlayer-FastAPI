from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class FollowingBase(BaseModel):
    """Base schema for following operations"""
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
    """Schema for creating a new following"""
    pass


class FollowingOut(FollowingBase):
    """Schema for following output"""
    id: int
    started_at: datetime

    class Config:
        from_attributes = True


class FollowingToggle(BaseModel):
    """Schema for toggling follow status"""
    artist_id: Optional[int] = None
    band_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_toggle_target(self) -> "FollowingToggle":
        """Ensure either artist_id or band_id is provided, but not both"""
        if self.artist_id is not None and self.band_id is not None:
            raise ValueError("Cannot toggle both artist and band simultaneously")
        if self.artist_id is None and self.band_id is None:
            raise ValueError("Must specify either artist_id or band_id")
        return self


class ArtistMinimal(BaseModel):
    """Minimal artist information for following relationships"""
    id: int
    artist_stage_name: str
    artist_profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class BandMinimal(BaseModel):
    """Minimal band information for following relationships"""
    id: int
    name: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True


class FollowingWithTarget(BaseModel):
    """Following with target details (artist or band)"""
    id: int
    user_id: int
    started_at: datetime
    artist: Optional[ArtistMinimal] = None
    band: Optional[BandMinimal] = None

    class Config:
        from_attributes = True


class FollowingList(BaseModel):
    """Paginated list of followings"""
    followings: List[FollowingWithTarget]
    total: int
    page: int
    per_page: int
    total_pages: int


class FollowingStats(BaseModel):
    """Following statistics"""
    total_followings: int
    unique_users: int
    unique_artists: int
    unique_bands: int
    most_followed_artist: Optional[ArtistMinimal] = None
    most_followed_band: Optional[BandMinimal] = None


class UserFollowingSummary(BaseModel):
    """User's following summary"""
    user_id: int
    total_following: int
    artist_count: int
    band_count: int
    followed_artists: List[ArtistMinimal]
    followed_bands: List[BandMinimal] 
