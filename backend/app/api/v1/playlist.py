from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.db.models.user import User
from app.schemas.playlist import (
    PlaylistCreate, PlaylistUpdate, PlaylistOut, PlaylistWithOwner,
    PlaylistList, PlaylistListWithOwner, PlaylistStats
)
from app.crud.playlist import (
    create_playlist, get_playlist_by_id, get_playlist_with_owner,
    get_user_playlists, get_user_playlists_with_owner, search_playlists,
    update_playlist, delete_playlist, user_can_edit_playlist,
    user_can_view_playlist, get_playlist_stats, get_user_playlist_stats
)

router = APIRouter()


@router.post("/", response_model=PlaylistOut)
def create_new_playlist(
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new playlist
    """
    try:
        playlist = create_playlist(db, playlist_data, current_user.id)
        return playlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my", response_model=PlaylistList)
def get_my_playlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's playlists
    """
    playlists, total = get_user_playlists(db, current_user.id, skip, limit)
    
    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PlaylistList(
        playlists=playlists,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/my/with-owner", response_model=PlaylistListWithOwner)
def get_my_playlists_with_owner(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's playlists with owner details
    """
    playlists, total = get_user_playlists_with_owner(db, current_user.id, skip, limit)
    
    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PlaylistListWithOwner(
        playlists=playlists,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/search", response_model=PlaylistList)
def search_my_playlists(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search current user's playlists
    """
    playlists, total = search_playlists(db, q, current_user.id, skip, limit)
    
    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PlaylistList(
        playlists=playlists,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.get("/{playlist_id}", response_model=PlaylistWithOwner)
def get_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific playlist by ID
    """
    playlist = get_playlist_with_owner(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if not user_can_view_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return playlist


@router.put("/{playlist_id}", response_model=PlaylistOut)
def update_playlist_info(
    playlist_id: int,
    playlist_data: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update playlist information
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        playlist = update_playlist(db, playlist_id, playlist_data)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{playlist_id}")
def delete_playlist_by_id(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = delete_playlist(db, playlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    return {"message": "Playlist deleted successfully"}


@router.get("/my/stats", response_model=PlaylistStats)
def get_my_playlist_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's playlist statistics
    """
    stats = get_user_playlist_stats(db, current_user.id)
    return stats


@router.get("/{playlist_id}/stats", response_model=PlaylistStats)
def get_playlist_statistics(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get playlist statistics
    """
    if not user_can_view_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        stats = get_playlist_stats(db, playlist_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
