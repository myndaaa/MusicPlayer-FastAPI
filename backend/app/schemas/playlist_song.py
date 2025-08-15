from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PlaylistSongBase(BaseModel):
    song_id: int
    song_order: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistSongCreate(PlaylistSongBase):
    pass


class PlaylistSongUpdate(BaseModel):
    song_order: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistSongOut(PlaylistSongBase):
    id: int
    playlist_id: int

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


class PlaylistSongWithSong(PlaylistSongOut):
    song: SongMinimal

    class Config:
        from_attributes = True


class PlaylistSongList(BaseModel):
    songs: List[PlaylistSongWithSong]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistSongAdd(BaseModel):
    song_id: int
    song_order: Optional[int] = None


class PlaylistSongReorder(BaseModel):
    song_id: int
    new_order: int


class PlaylistSongBulkReorder(BaseModel):
    song_orders: List[PlaylistSongReorder]


class PlaylistSongStats(BaseModel):
    total_songs: int
    total_duration: int  # in seconds
    average_song_duration: float
    shortest_song: Optional[SongMinimal] = None
    longest_song: Optional[SongMinimal] = None
    most_common_artist: Optional[str] = None
    most_common_genre: Optional[str] = None 
