from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_user, get_current_admin
from app.db.models.user import User
from app.schemas.history import (
    HistoryWithSong, HistoryList, HistoryToggle, HistoryStats, GlobalHistoryStats
)
from app.crud.history import (
    create_history_entry, get_user_history, clear_user_history,
    get_user_history_stats, get_global_history_stats, count_song_plays
)
from app.crud.song import get_song_by_id

router = APIRouter()


@router.get("/song/{song_id}/plays", response_model=int)
def get_song_play_count(song_id: int, db: Session = Depends(get_db)):
    """
    Get total play count for a specific song (public endpoint)
    """
    song = get_song_by_id(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    return count_song_plays(db, song_id)


@router.post("/add", response_model=HistoryWithSong)
def add_history_entry(
    history_data: HistoryToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a song to user's listening history (authenticated users only)
    """
    song = get_song_by_id(db, history_data.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    history_entry = create_history_entry(db, current_user.id, history_data.song_id)
    
    if not history_entry:
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please wait before playing this song again."
        )
    
    return HistoryWithSong(
        id=history_entry.id,
        user_id=history_entry.user_id,
        song_id=history_entry.song_id,
        played_at=history_entry.played_at,
        is_cleared=history_entry.is_cleared,
        song=song
    )


@router.get("/my", response_model=HistoryList)
def get_my_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's listening history (authenticated users only)
    """
    skip = (page - 1) * per_page
    history, total = get_user_history(db, current_user.id, skip, per_page)
    
    history_with_songs = []
    for entry in history:
        history_with_songs.append(HistoryWithSong(
            id=entry.id,
            user_id=entry.user_id,
            song_id=entry.song_id,
            played_at=entry.played_at,
            is_cleared=entry.is_cleared,
            song=entry.song
        ))
    
    total_pages = (total + per_page - 1) // per_page
    
    return HistoryList(
        history=history_with_songs,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/my/stats", response_model=HistoryStats)
def get_my_history_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's listening statistics (authenticated users only)
    """
    return get_user_history_stats(db, current_user.id)


@router.delete("/my/clear")
def clear_my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Clear current user's listening history (authenticated users only)
    """
    cleared_count = clear_user_history(db, current_user.id)
    
    return {
        "message": f"Successfully cleared {cleared_count} history entries",
        "cleared_count": cleared_count
    }


@router.get("/admin/stats", response_model=GlobalHistoryStats)
def get_global_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Get global listening statistics (admin only)
    """
    return get_global_history_stats(db)
