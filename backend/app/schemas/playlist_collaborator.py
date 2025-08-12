from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PlaylistCollaboratorBase(BaseModel):
    playlist_id: int
    collaborator_id: int
    can_edit: bool = False
    added_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistCollaboratorCreate(PlaylistCollaboratorBase):
    pass


class PlaylistCollaboratorUpdate(PlaylistCollaboratorBase):
    playlist_id: Optional[int] = None
    collaborator_id: Optional[int] = None
    can_edit: Optional[bool] = None
    added_by_user_id: Optional[int] = None


class PlaylistCollaboratorOut(PlaylistCollaboratorBase):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True


class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True



class PlaylistCollaboratorWithUser(PlaylistCollaboratorOut):
    collaborator: UserMinimal
    added_by: Optional[UserMinimal] = None

    class Config:
        from_attributes = True



class PlaylistCollaboratorList(BaseModel):
    collaborators: List[PlaylistCollaboratorWithUser]
    total: int
    page: int
    per_page: int
    total_pages: int



class PlaylistCollaboratorAdd(BaseModel):
    collaborator_id: int
    can_edit: bool = False


class PlaylistCollaboratorUpdatePermissions(BaseModel):
    can_edit: bool



class PlaylistCollaboratorStats(BaseModel):
    total_collaborators: int
    can_edit_collaborators: int
    read_only_collaborators: int
    most_collaborative_user: Optional[UserMinimal] = None 
