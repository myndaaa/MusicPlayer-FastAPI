from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.playlist_collaborator import (
    PlaylistCollaboratorCreate, PlaylistCollaboratorList, PlaylistCollaboratorStats
)
from app.crud.playlist import user_can_edit_playlist, access_playlist_by_token, generate_collaboration_link
from app.crud.playlist_collaborator import (
    add_collaborator_to_playlist, get_playlist_collaborators, remove_collaborator_from_playlist,
    get_playlist_collaborator_stats
)
from app.crud.user import get_user_by_username

router = APIRouter()


@router.post("/{playlist_id}/collaborate")
def generate_collaboration_link_endpoint(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a collaboration link for the playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        collaboration_link = generate_collaboration_link(db, playlist_id)
        return {"collaboration_link": collaboration_link}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{playlist_id}/collaborators/{username}")
def add_collaborator_endpoint(
    playlist_id: int,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a collaborator to a playlist by username
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        collaborator = add_collaborator_to_playlist(
            db, playlist_id, user.id, current_user.id, can_edit=True
        )
        return {"message": f"Added {username} as collaborator"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{playlist_id}/collaborators/{username}")
def remove_collaborator_endpoint(
    playlist_id: int,
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a collaborator from a playlist by username
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = remove_collaborator_from_playlist(db, playlist_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Collaborator not found")
    
    return {"message": f"Removed {username} as collaborator"}


@router.get("/{playlist_id}/collaborators", response_model=PlaylistCollaboratorList)
def get_playlist_collaborators_endpoint(
    playlist_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all collaborators for a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    collaborators, total = get_playlist_collaborators(db, playlist_id, skip, limit)
    
    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PlaylistCollaboratorList(
        collaborators=collaborators,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/{playlist_id}/collaborators/stats", response_model=PlaylistCollaboratorStats)
def get_playlist_collaborator_statistics(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get playlist collaborator statistics
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return get_playlist_collaborator_stats(db, playlist_id)


@router.get("/collaborate/{token}")
def access_playlist_via_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Access a playlist via collaboration token
    """
    playlist = access_playlist_by_token(db, token)
    if not playlist:
        raise HTTPException(status_code=404, detail="Invalid or expired collaboration link")
    
    return {
        "playlist_id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "owner_id": playlist.owner_id,
        "message": "Use this token to join the playlist as a collaborator"
    }
