from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class HistoryBase(BaseModel):
    user_id: int
    song_id: int
    played_at: datetime
    is_cleared: bool = False

    class Config:
        from_attributes = True

class HistoryCreate(HistoryBase):
    pass


class HistoryOut(HistoryBase):
    id: int

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



class HistoryWithSong(HistoryOut):
    song: SongMinimal

    class Config:
        from_attributes = True



class HistoryList(BaseModel):
    history: List[HistoryWithSong]
    total: int
    page: int
    per_page: int
    total_pages: int



class HistoryToggle(BaseModel):
    song_id: int



class HistoryStats(BaseModel):
    total_listens: int
    unique_songs: int
    total_duration: int  # in seconds
    most_listened_song: Optional[SongMinimal] = None
    most_listened_artist: Optional[str] = None
    most_listened_genre: Optional[str] = None
    listening_streak: int  # consecutive days
    last_listened: Optional[datetime] = None



class GlobalHistoryStats(BaseModel):
    total_listens: int
    unique_songs: int
    unique_users: int
    most_listened_song: Optional[SongMinimal] = None
    most_listened_artist: Optional[str] = None
    most_listened_genre: Optional[str] = None
    average_listens_per_user: float 
