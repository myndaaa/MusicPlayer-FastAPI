from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class ArtistBandMemberBase(BaseModel):
    artist_id: int
    band_id: int
    joined_on: datetime
    left_at: Optional[datetime] = None
    is_current_member: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "ArtistBandMemberBase":
        """Ensure left_at is after joined_on if provided"""
        if self.left_at and self.left_at <= self.joined_on:
            raise ValueError("left_at must be after joined_on")
        return self

    class Config:
        from_attributes = True


class ArtistBandMemberCreate(ArtistBandMemberBase):
    pass


class ArtistBandMemberOut(ArtistBandMemberBase):
    band_member_id: int

    class Config:
        from_attributes = True


class ArtistBandMemberJoin(BaseModel):
    band_id: int
    joined_on: Optional[datetime] = None


class ArtistBandMemberLeave(BaseModel):
    band_id: int
    left_at: Optional[datetime] = None


class ArtistBandMemberRejoin(BaseModel):
    band_id: int
    joined_on: Optional[datetime] = None


class ArtistBandMemberInvite(BaseModel):
    artist_id: int
    joined_on: Optional[datetime] = None


class ArtistBandMemberRemove(BaseModel):
    artist_id: int
    left_at: Optional[datetime] = None


class ArtistBandMemberStats(BaseModel):
    total_memberships: int
    current_memberships: int
    former_memberships: int
    average_membership_duration: float 
