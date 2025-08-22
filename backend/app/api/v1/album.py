"""
Album API endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, get_current_admin
from app.crud.album import (
    create_album, get_album_by_id, get_all_albums, update_album,
    get_albums_by_artist, get_albums_by_band, get_albums_by_title,
    get_albums_by_artist_name, get_albums_by_band_name,
    get_albums_released_between, get_albums_by_user,
    get_album_with_songs, get_album_count, album_exists
)
from app.schemas.album import (
    AlbumCreate, AlbumUpdate, AlbumOut, AlbumWithRelations,
    AlbumList, AlbumListWithRelations, AlbumFilter, AlbumSearch, AlbumStats
)
from app.db.models.user import User

router = APIRouter()


@router.post("/", response_model=AlbumOut)
async def create_album_endpoint(
    album_data: AlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new album.
    
    - **current_user**: Authenticated user (admin or musician)
    """
    if current_user.role not in ["admin", "musician"]:
        raise HTTPException(status_code=403, detail="Only admins and musicians can create albums")
    
    try:
        album = create_album(db, album_data, current_user.id)
        return album
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{album_id}", response_model=AlbumWithRelations)
async def get_album_endpoint(
    album_id: int,
    db: Session = Depends(get_db)
):
    """
    Get album by ID with relationships.
    
    - **album_id**: ID of the album to retrieve
    """
    album = get_album_with_songs(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return album


@router.put("/{album_id}", response_model=AlbumOut)
async def update_album_endpoint(
    album_id: int,
    album_data: AlbumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update album information.
    
    - **album_id**: ID of the album to update
    - **current_user**: Authenticated user (admin or album owner)
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    if current_user.role != "admin" and album.uploaded_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this album")
    
    updated_album = update_album(db, album_id, album_data)
    if not updated_album:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return updated_album


@router.get("/", response_model=AlbumListWithRelations)
async def get_albums_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of all albums with relationships.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_all_albums(db, skip, limit)
    total = get_album_count(db)
    
    return AlbumListWithRelations(
        albums=albums,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/artist/{artist_id}", response_model=List[AlbumOut])
async def get_albums_by_artist_endpoint(
    artist_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get albums by artist ID.
    
    - **artist_id**: ID of the artist
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_albums_by_artist(db, artist_id, skip, limit)
    return albums


@router.get("/band/{band_id}", response_model=List[AlbumOut])
async def get_albums_by_band_endpoint(
    band_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get albums by band ID.
    
    - **band_id**: ID of the band
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_albums_by_band(db, band_id, skip, limit)
    return albums


@router.get("/search/title", response_model=List[AlbumOut])
async def search_albums_by_title_endpoint(
    title: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search albums by title.
    
    - **title**: Title to search for
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_albums_by_title(db, title, skip, limit)
    return albums


@router.get("/search/artist", response_model=List[AlbumOut])
async def search_albums_by_artist_name_endpoint(
    artist_name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search albums by artist name.
    
    - **artist_name**: Artist name to search for
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_albums_by_artist_name(db, artist_name, skip, limit)
    return albums


@router.get("/search/band", response_model=List[AlbumOut])
async def search_albums_by_band_name_endpoint(
    band_name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search albums by band name.
    
    - **band_name**: Band name to search for
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    albums = get_albums_by_band_name(db, band_name, skip, limit)
    return albums


@router.get("/user/{user_id}", response_model=List[AlbumOut])
async def get_albums_by_user_endpoint(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get albums uploaded by a specific user.
    
    - **user_id**: ID of the user
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **current_user**: Authenticated user (admin or same user)
    """
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's albums")
    
    albums = get_albums_by_user(db, user_id, skip, limit)
    return albums


@router.get("/admin/stats", response_model=AlbumStats)
async def get_album_statistics_endpoint(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get album statistics for admin dashboard.
    
    - **current_admin**: Authenticated admin user
    """
    # This would need to be implemented in the CRUD
    total_albums = get_album_count(db)
    
    return AlbumStats(
        total_albums=total_albums,
        albums_by_artist=0,  # TODO: Implement
        albums_by_band=0,   
        most_uploaded_artist=None,  
        most_uploaded_band=None     
    )
