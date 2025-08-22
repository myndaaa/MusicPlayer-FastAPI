from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class LikeBase(BaseModel):
    """Base schema for like operations"""
    user_id: int
    song_id: int

    class Config:
        from_attributes = True


class LikeCreate(LikeBase):
    """Schema for creating a new like"""
    pass


class LikeOut(LikeBase):
    """Schema for like output"""
    id: int
    liked_at: datetime

    class Config:
        from_attributes = True


class UserMinimal(BaseModel):
    """Minimal user information for like relationships"""
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class SongMinimal(BaseModel):
    """Minimal song information for like relationships"""
    id: int
    title: str
    song_duration: int
    cover_image: Optional[str] = None
    artist_name: Optional[str] = None
    band_name: Optional[str] = None

    class Config:
        from_attributes = True


class LikeList(BaseModel):
    """Paginated list of likes"""
    likes: List[LikeOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class LikeToggle(BaseModel):
    """Schema for toggling like status"""
    song_id: int


class LikeStats(BaseModel):
    """Like statistics"""
    total_likes: int
    unique_songs: int
    unique_users: int
    most_liked_song: Optional[SongMinimal] = None
    most_liked_artist: Optional[str] = None
    most_liked_genre: Optional[str] = None


class UserLikesSummary(BaseModel):
    """Summary of user's likes"""
    user_id: int
    total_likes: int
    liked_songs: List[SongMinimal]
    favorite_artists: List[str]
    favorite_genres: List[str]


class LikeWithSong(BaseModel):
    """Like with full song details for Flutter widgets."""
    id: int
    user_id: int
    song_id: int
    liked_at: datetime
    song: SongMinimal

    class Config:
        from_attributes = True


class LikeListWithSongs(BaseModel):
    """Paginated list of likes with full song details."""
    likes: List[LikeWithSong]
    total: int
    page: int
    per_page: int
    total_pages: int 
