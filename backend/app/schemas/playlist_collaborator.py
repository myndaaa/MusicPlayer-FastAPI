from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


# Base schema for playlist collaborator
class PlaylistCollaboratorBase(BaseModel):
    playlist_id: int
    collaborator_id: int
    can_edit: bool = False
    added_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class PlaylistCollaboratorCreate(PlaylistCollaboratorBase):
    pass


class PlaylistCollaboratorUpdate(BaseModel):
    can_edit: Optional[bool] = None

    class Config:
        from_attributes = True


class PlaylistCollaboratorOut(PlaylistCollaboratorBase):
    id: int
    added_at: datetime

    class Config:
        from_attributes = True


# Schemas for relationships
class PlaylistMinimal(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
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


# Playlist collaborator output with relationships
class PlaylistCollaboratorWithRelations(PlaylistCollaboratorOut):
    playlist: PlaylistMinimal
    collaborator: UserMinimal
    added_by: Optional[UserMinimal] = None


# Playlist collaboration list
class PlaylistCollaborationList(BaseModel):
    playlist_id: int
    collaborators: List[PlaylistCollaboratorWithRelations]
    total_collaborators: int
    can_edit_count: int
    read_only_count: int


# User collaboration list
class UserCollaborationList(BaseModel):
    user_id: int
    collaborations: List[PlaylistCollaboratorWithRelations]
    owned_playlists: List[PlaylistMinimal]
    total_collaborations: int
    can_edit_count: int
    read_only_count: int


# List schemas for pagination
class PlaylistCollaboratorList(BaseModel):
    collaborators: List[PlaylistCollaboratorOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class PlaylistCollaboratorListWithRelations(BaseModel):
    collaborators: List[PlaylistCollaboratorWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class PlaylistCollaboratorFilter(BaseModel):
    playlist_id: Optional[int] = None
    collaborator_id: Optional[int] = None
    added_by_user_id: Optional[int] = None
    can_edit: Optional[bool] = None
    added_at_from: Optional[datetime] = None
    added_at_to: Optional[datetime] = None


# Collaboration management schemas
class PlaylistCollaboratorAdd(BaseModel):
    playlist_id: int
    collaborator_id: int
    can_edit: bool = False


class PlaylistCollaboratorRemove(BaseModel):
    playlist_id: int
    collaborator_id: int


class PlaylistCollaboratorUpdatePermissions(BaseModel):
    playlist_id: int
    collaborator_id: int
    can_edit: bool


class PlaylistCollaboratorBulkAdd(BaseModel):
    playlist_id: int
    collaborators: List[PlaylistCollaboratorAdd]


class PlaylistCollaboratorBulkRemove(BaseModel):
    playlist_id: int
    collaborator_ids: List[int]


class PlaylistCollaboratorBulkUpdate(BaseModel):
    playlist_id: int
    updates: List[dict]  # TODO HINT:  [{"collaborator_id": 1, "can_edit": true}, ...]


# Collaboration invitation schemas
class PlaylistCollaboratorInvite(BaseModel):
    playlist_id: int
    collaborator_email: str
    can_edit: bool = False
    message: Optional[str] = None


class PlaylistCollaboratorInviteResponse(BaseModel):
    invite_id: int
    accept: bool
    message: Optional[str] = None


# Collaboration statistics
class PlaylistCollaboratorStats(BaseModel):
    total_collaborations: int
    active_collaborations: int
    can_edit_collaborations: int
    read_only_collaborations: int
    most_collaborative_playlist: Optional[PlaylistMinimal] = None
    most_collaborative_user: Optional[UserMinimal] = None


# Collaboration validation schema
class PlaylistCollaboratorValidation(BaseModel):
    playlist_id: int
    collaborator_id: int

    @model_validator(mode="after")
    def validate_unique_collaboration(self) -> "PlaylistCollaboratorValidation":
        """Ensure user is not already a collaborator on this playlist"""
        # TODO:  validation would be done in the service layer
        return self


# Collaboration search
class PlaylistCollaboratorSearch(BaseModel):
    playlist_id: Optional[int] = None
    query: str  # Search in collaborator username, first_name, and last_name
    can_edit: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Collaboration export
class PlaylistCollaboratorExport(BaseModel):
    playlist_id: Optional[int] = None
    user_id: Optional[int] = None
    format: str = "json"  
    include_permissions: bool = True
    include_timestamps: bool = True


# Collaboration notifications
class PlaylistCollaboratorNotification(BaseModel):
    playlist_id: int
    collaborator_id: int
    notification_type: str  # "added", "removed", "permission_changed"
    message: str
    timestamp: datetime


# Collaboration activity
class PlaylistCollaboratorActivity(BaseModel):
    playlist_id: int
    activities: List[dict]  # Timeline 
    # TODO HINT:  [{"date": "2024-01-01", "action": "added", "user": {...}}, ...] 
