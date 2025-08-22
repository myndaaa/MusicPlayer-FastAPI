from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.playlist_song import (
    PlaylistSongAdd, PlaylistSongReorder, PlaylistSongBulkReorder,
    PlaylistSongList, PlaylistSongStats
)
from app.crud.playlist import user_can_edit_playlist, user_can_view_playlist
from app.crud.playlist_song import (
    add_song_to_playlist, get_songs_in_playlist, remove_song_from_playlist,
    reorder_playlist_song, reorder_playlist_bulk, clear_playlist,
    get_playlist_song_stats
)
from app.crud.song import get_song_by_id

router = APIRouter()


@router.post("/{playlist_id}/songs", response_model=PlaylistSongList)
def add_song_to_playlist_endpoint(
    playlist_id: int,
    song_data: PlaylistSongAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a song to a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")


    song = get_song_by_id(db, song_data.song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    try:
        add_song_to_playlist(db, playlist_id, song_data.song_id, song_data.song_order)


        songs, total = get_songs_in_playlist(db, playlist_id)
        return PlaylistSongList(
            songs=songs,
            total=total,
            page=1,
            per_page=total,
            total_pages=1
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{playlist_id}/songs", response_model=PlaylistSongList)
def get_playlist_songs(
    playlist_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get songs in a playlist
    """
    if not user_can_view_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    songs, total = get_songs_in_playlist(db, playlist_id, skip, limit)

    total_pages = (total + limit - 1) // limit
    page = (skip // limit) + 1

    return PlaylistSongList(
        songs=songs,
        total=total,
        page=page,
        per_page=limit,
        total_pages=total_pages
    )


@router.put("/{playlist_id}/songs/reorder")
def reorder_playlist_song_endpoint(
    playlist_id: int,
    reorder_data: PlaylistSongReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reorder a song in a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    playlist_song = reorder_playlist_song(db, playlist_id, reorder_data.song_id, reorder_data.new_order)
    if not playlist_song:
        raise HTTPException(status_code=404, detail="Song not found in playlist")

    return {"message": "Song reordered successfully"}


@router.put("/{playlist_id}/songs/reorder-bulk")
def reorder_playlist_songs_bulk(
    playlist_id: int,
    reorder_data: PlaylistSongBulkReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk reorder songs in a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Convert to list of dicts for the CRUD function
    song_orders = [{"song_id": item.song_id, "new_order": item.new_order} for item in reorder_data.song_orders]

    success = reorder_playlist_bulk(db, playlist_id, song_orders)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reorder songs")

    return {"message": "Songs reordered successfully"}


@router.delete("/{playlist_id}/songs/{song_id}")
def remove_song_from_playlist_endpoint(
    playlist_id: int,
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a song from a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    success = remove_song_from_playlist(db, playlist_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Song not found in playlist")

    return {"message": "Song removed from playlist"}


@router.delete("/{playlist_id}/songs")
def clear_playlist_songs(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove all songs from a playlist
    """
    if not user_can_edit_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    removed_count = clear_playlist(db, playlist_id)
    return {"message": f"Removed {removed_count} songs from playlist"}


@router.get("/{playlist_id}/songs/stats", response_model=PlaylistSongStats)
def get_playlist_song_statistics(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get playlist song statistics
    """
    if not user_can_view_playlist(db, current_user.id, playlist_id):
        raise HTTPException(status_code=403, detail="Access denied")

    return get_playlist_song_stats(db, playlist_id)
