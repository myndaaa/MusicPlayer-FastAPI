from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field


# Base schema for like
class LikeBase(BaseModel):
    user_id: int
    song_id: int

    class Config:
        from_attributes = True


class LikeCreate(LikeBase):
    pass


class LikeUpdate(BaseModel):
    liked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LikeOut(LikeBase):
    id: int
    liked_at: datetime

    class Config:
        from_attributes = True


# Nested schemas for relationships
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
    artist_name: Optional[str] = None
    band_name: Optional[str] = None

    class Config:
        from_attributes = True


# like output with relationships
class LikeWithRelations(LikeOut):
    user: UserMinimal
    song: SongMinimal


# List schemas for pagination
class LikeList(BaseModel):
    likes: List[LikeOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class LikeListWithRelations(BaseModel):
    likes: List[LikeWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class LikeFilter(BaseModel):
    user_id: Optional[int] = None
    song_id: Optional[int] = None
    liked_at_from: Optional[datetime] = None
    liked_at_to: Optional[datetime] = None


class LikeSearch(BaseModel):
    user_id: int
    query: Optional[str] = None  # Search in song title, artist, or band name
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Like management schemas
class LikeAdd(BaseModel):
    user_id: int
    song_id: int


class LikeRemove(BaseModel):
    user_id: int
    song_id: int


class LikeToggle(BaseModel):
    user_id: int
    song_id: int


# Like statistics
class LikeStats(BaseModel):
    total_likes: int
    unique_songs: int
    unique_users: int
    most_liked_song: Optional[SongMinimal] = None
    most_liked_artist: Optional[str] = None
    most_liked_genre: Optional[str] = None


# User likes summary
class UserLikesSummary(BaseModel):
    user_id: int
    total_likes: int
    liked_songs: List[SongMinimal]
    favorite_artists: List[str]
    favorite_genres: List[str]


# Song likes summary
class SongLikesSummary(BaseModel):
    song_id: int
    total_likes: int
    liked_by_users: List[UserMinimal]
    like_percentage: float  # Percentage of users who liked this song


# Like export schema
class LikeExport(BaseModel):
    user_id: int
    format: str = "json"  # json, csv, etc.
    include_song_details: bool = True


# Like recommendations
class LikeRecommendation(BaseModel):
    user_id: int
    recommended_songs: List[SongMinimal]
    recommendation_reason: str  #  "Based on your likes", "Popular among similar users"
    confidence_score: float  # 0.0 to 1.0 
