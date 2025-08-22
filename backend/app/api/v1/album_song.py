"""
AlbumSong API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.album_song import (
    create_album_song, get_album_song_by_id, get_album_songs_by_album,
    update_album_song, delete_album_song, delete_album_song_by_album_and_song,
    get_album_song_statistics, reorder_album_tracks
)
from app.crud.album import get_album_by_id
from app.schemas.album_song import (
    AlbumSongCreate, AlbumSongUpdate, AlbumSongOut, AlbumSongWithRelations,
    AlbumSongList, AlbumSongListWithRelations, AlbumSongAdd,
    AlbumSongBulkAdd, AlbumSongBulkReorder, AlbumSongStats
)
from app.db.models.user import User

router = APIRouter()


@router.post("/{album_id}/songs", response_model=AlbumSongOut)
async def add_song_to_album_endpoint(
    album_id: int,
    song_data: AlbumSongAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a song to an album.
    
    - **album_id**: ID of the album
    - **song_data**: Song data with track number
    - **current_user**: Authenticated user (admin or album owner)
    """
    # Check if album exists
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add songs to this album")
    
    try:
        album_song_data = AlbumSongCreate(
            album_id=album_id,
            song_id=song_data.song_id,
            track_number=song_data.track_number
        )
        album_song = create_album_song(db, album_song_data)
        return album_song
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{album_id}/songs/bulk", response_model=List[AlbumSongOut])
async def add_songs_to_album_bulk_endpoint(
    album_id: int,
    songs_data: AlbumSongBulkAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add multiple songs to an album.
    
    - **album_id**: ID of the album
    - **songs_data**: List of songs with track numbers
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add songs to this album")
    
    try:
        album_songs = []
        for song_data in songs_data.songs:
            album_song_data = AlbumSongCreate(
                album_id=album_id,
                song_id=song_data.song_id,
                track_number=song_data.track_number
            )
            album_song = create_album_song(db, album_song_data)
            album_songs.append(album_song)
        return album_songs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{album_id}/songs", response_model=List[AlbumSongWithRelations])
async def get_album_songs_endpoint(
    album_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all songs in an album.
    
    - **album_id**: ID of the album
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    album_songs = get_album_songs_by_album(db, album_id, skip, limit)
    return album_songs


@router.put("/{album_id}/songs/reorder", response_model=List[AlbumSongOut])
async def reorder_album_songs_endpoint(
    album_id: int,
    reorder_data: AlbumSongBulkReorder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk reorder songs in an album.
    
    - **album_id**: ID of the album
    - **reorder_data**: List of songs with new track numbers
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reorder this album")
    
    try:
        track_orders = [
            {"song_id": track.song_id, "track_number": track.track_number}
            for track in reorder_data.tracks
        ]
        
        success = reorder_album_tracks(db, album_id, track_orders)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder tracks")
        
        album_songs = get_album_songs_by_album(db, album_id)
        return album_songs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{album_id}/songs/{album_song_id}", response_model=AlbumSongOut)
async def update_album_song_endpoint(
    album_id: int,
    album_song_id: int,
    song_data: AlbumSongUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update track number for a song in an album.
    
    - **album_id**: ID of the album
    - **album_song_id**: ID of the album-song relationship
    - **song_data**: New track number
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this album")
    
    try:
        updated_album_song = update_album_song(db, album_song_id, song_data)
        if not updated_album_song:
            raise HTTPException(status_code=404, detail="Album-song relationship not found")
        return updated_album_song
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{album_id}/songs/{song_id}")
async def remove_song_from_album_endpoint(
    album_id: int,
    song_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a song from an album.
    
    - **album_id**: ID of the album
    - **song_id**: ID of the song to remove
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to remove songs from this album")
    
    success = delete_album_song_by_album_and_song(db, album_id, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="Song not found in album")
    
    return {"message": "Song removed from album successfully"}


@router.delete("/{album_id}/songs")
async def clear_album_songs_endpoint(
    album_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove all songs from an album.
    
    - **album_id**: ID of the album
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to clear songs from this album")
    
    album_songs = get_album_songs_by_album(db, album_id)
    for album_song in album_songs:
        delete_album_song(db, album_song.id)
    
    return {"message": "All songs removed from album successfully"}


@router.get("/{album_id}/songs/stats", response_model=AlbumSongStats)
async def get_album_song_statistics_endpoint(
    album_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for songs in an album.
    
    - **album_id**: ID of the album
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    stats = get_album_song_statistics(db, album_id)
    return AlbumSongStats(**stats)
