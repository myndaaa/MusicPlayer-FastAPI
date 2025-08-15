from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PlaylistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(PlaylistBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = Field(None, max_length=255)


class PlaylistOut(PlaylistBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class PlaylistWithOwner(PlaylistOut):
    owner: UserMinimal

    class Config:
        from_attributes = True


class PlaylistList(BaseModel):
    playlists: List[PlaylistOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistListWithOwner(BaseModel):
    playlists: List[PlaylistWithOwner]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistStats(BaseModel):
    total_playlists: int
    total_owned_playlists: int
    total_collaborated_playlists: int
    created_at: datetime
    last_modified: Optional[datetime] = None 
