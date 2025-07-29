from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# Base schema for artist-band member relationship
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


class ArtistBandMemberUpdate(BaseModel):
    left_at: Optional[datetime] = None
    is_current_member: Optional[bool] = None

    class Config:
        from_attributes = True


class ArtistBandMemberOut(ArtistBandMemberBase):
    band_member_id: int

    class Config:
        from_attributes = True


# Nested schemas for relationships
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


# artist-band member output with relationships
class ArtistBandMemberWithRelations(ArtistBandMemberOut):
    artist: ArtistMinimal
    band: BandMinimal


# Band membership list
class BandMembershipList(BaseModel):
    band_id: int
    members: List[ArtistBandMemberWithRelations]
    current_members: List[ArtistBandMemberWithRelations]
    former_members: List[ArtistBandMemberWithRelations]
    total_members: int
    current_member_count: int


# Artist membership list
class ArtistMembershipList(BaseModel):
    artist_id: int
    bands: List[ArtistBandMemberWithRelations]
    current_bands: List[ArtistBandMemberWithRelations]
    former_bands: List[ArtistBandMemberWithRelations]
    total_bands: int
    current_band_count: int


# List schemas for pagination
class ArtistBandMemberList(BaseModel):
    memberships: List[ArtistBandMemberOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class ArtistBandMemberListWithRelations(BaseModel):
    memberships: List[ArtistBandMemberWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class ArtistBandMemberFilter(BaseModel):
    artist_id: Optional[int] = None
    band_id: Optional[int] = None
    is_current_member: Optional[bool] = None
    joined_on_from: Optional[datetime] = None
    joined_on_to: Optional[datetime] = None
    left_at_from: Optional[datetime] = None
    left_at_to: Optional[datetime] = None


# Membership management schemas
class ArtistBandMemberAdd(BaseModel):
    artist_id: int
    band_id: int
    joined_on: Optional[datetime] = None  


class ArtistBandMemberLeave(BaseModel):
    artist_id: int
    band_id: int
    left_at: Optional[datetime] = None  


class ArtistBandMemberRejoin(BaseModel):
    artist_id: int
    band_id: int
    joined_on: Optional[datetime] = None  # If None, use current time


class ArtistBandMemberBulkAdd(BaseModel):
    band_id: int
    artists: List[ArtistBandMemberAdd]


class ArtistBandMemberBulkRemove(BaseModel):
    band_id: int
    artist_ids: List[int]


# Membership statistics
class ArtistBandMemberStats(BaseModel):
    total_memberships: int
    current_memberships: int
    former_memberships: int
    average_membership_duration: float  # in days
    longest_membership: Optional[ArtistBandMemberWithRelations] = None
    shortest_membership: Optional[ArtistBandMemberWithRelations] = None


# Band member timeline
class BandMemberTimeline(BaseModel):
    band_id: int
    timeline: List[dict]  # Timeline of member changes
   


# Artist band timeline
class ArtistBandTimeline(BaseModel):
    artist_id: int
    timeline: List[dict]  # Timeline of band changes
   

# Membership validation schema
class ArtistBandMemberValidation(BaseModel):
    artist_id: int
    band_id: int

    @model_validator(mode="after")
    def validate_unique_membership(self) -> "ArtistBandMemberValidation":
        """Ensure artist is not already a current member of this band"""
        # TODO: To be done in the service layer
        return self


# Membership search
class ArtistBandMemberSearch(BaseModel):
    query: str  # Search in artist name or band name
    is_current_member: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Membership export
class ArtistBandMemberExport(BaseModel):
    band_id: Optional[int] = None
    artist_id: Optional[int] = None
    format: str = "json"  
    include_current_only: bool = False
    include_details: bool = True 
