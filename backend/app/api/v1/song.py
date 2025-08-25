from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_admin, get_current_musician
from app.schemas.song import (
    SongUploadByArtist, SongUploadByBand, SongUploadByAdmin, SongUpdate,
    SongOut, SongWithRelations, SongStats
)
from app.crud.song import (
    create_song_by_artist, create_song_by_band, create_song_by_admin,
    get_song_by_id, get_all_songs_paginated, search_songs,
    get_songs_by_artist, get_songs_by_band, get_songs_by_genre,
    update_song_file_path, update_song_metadata, disable_song, enable_song,
    song_exists, can_user_upload_for_band, get_song_statistics
)
from app.crud.user import get_user_by_id
from app.db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[SongOut])
async def get_all_songs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all active songs with pagination - public access"""
    return get_all_songs_paginated(db, skip=skip, limit=limit)


@router.get("/search", response_model=List[SongOut])
async def search_songs_endpoint(
    query: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Search songs by title, artist name, or band name - public access"""
    return search_songs(db, query, skip=skip, limit=limit)


@router.get("/{song_id}", response_model=SongOut)
async def get_song(song_id: int, db: Session = Depends(get_db)):
    """Get a specific song by ID - public access"""
    song = get_song_by_id(db, song_id)
    if not song or song.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    return song


@router.get("/artist/{artist_id}", response_model=List[SongOut])
async def get_songs_by_artist_endpoint(
    artist_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get songs by artist ID - public access"""
    return get_songs_by_artist(db, artist_id, skip=skip, limit=limit)


@router.get("/band/{band_id}", response_model=List[SongOut])
async def get_songs_by_band_endpoint(
    band_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get songs by band ID - public access"""
    return get_songs_by_band(db, band_id, skip=skip, limit=limit)


@router.get("/genre/{genre_id}", response_model=List[SongOut])
async def get_songs_by_genre_endpoint(
    genre_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get songs by genre ID - public access"""
    return get_songs_by_genre(db, genre_id, skip=skip, limit=limit)


@router.post("/artist/upload", response_model=SongOut, status_code=status.HTTP_201_CREATED)
async def upload_song_by_artist(
    song_data: SongUploadByArtist,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Upload a song as an artist - artist only"""
    # Verify the artist_id belongs to the current user
    from app.crud.artist import get_artist_by_user_id
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist or artist.id != song_data.artist_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload songs for your own artist profile"
        )
    
    return create_song_by_artist(db, song_data, current_user.id)


@router.post("/band/upload", response_model=SongOut, status_code=status.HTTP_201_CREATED)
async def upload_song_by_band(
    song_data: SongUploadByBand,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Upload a song as a band member - band member only"""
    # Check if user can upload for this band
    if not can_user_upload_for_band(db, current_user.id, song_data.band_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload songs for bands you are a member of"
        )
    
    return create_song_by_band(db, song_data, current_user.id)


@router.post("/admin/upload", response_model=SongOut, status_code=status.HTTP_201_CREATED)
async def upload_song_by_admin(
    song_data: SongUploadByAdmin,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload a song as admin (for any artist/band including dead artists) - admin only"""
    return create_song_by_admin(db, song_data, current_admin.id)


@router.put("/{song_id}/file-path", response_model=SongOut)
async def update_song_file_path_endpoint(
    song_id: int,
    file_path: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update song file path - admin only"""
    if not song_exists(db, song_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    updated_song = update_song_file_path(db, song_id, file_path)
    if not updated_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    return updated_song


@router.patch("/{song_id}/metadata", response_model=SongOut)
async def update_song_metadata_endpoint(
    song_id: int,
    song_data: SongUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update song metadata - admin only"""
    if not song_exists(db, song_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    updated_song = update_song_metadata(db, song_id, song_data)
    if not updated_song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    return updated_song


@router.post("/{song_id}/disable")
async def disable_song_endpoint(
    song_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Disable a song - admin only"""
    if not song_exists(db, song_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    success = disable_song(db, song_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    return {"message": "Song disabled successfully"}


@router.post("/{song_id}/enable")
async def enable_song_endpoint(
    song_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Enable a song - admin only"""
    if not song_exists(db, song_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    success = enable_song(db, song_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    return {"message": "Song enabled successfully"}


@router.get("/admin/statistics", response_model=SongStats)
async def get_song_statistics_endpoint(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get song statistics - admin only"""
    stats = get_song_statistics(db)
    return SongStats(**stats) 
