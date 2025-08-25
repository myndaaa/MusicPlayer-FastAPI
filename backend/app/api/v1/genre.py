from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_admin, get_current_user_optional
from app.schemas.genre import GenreCreate, GenreUpdate, GenreOut, GenreStats
from app.crud.genre import (
    create_genre, genre_exists, get_genre_by_id, get_genre_by_name, get_all_genres,
    get_all_active_genres, get_genres_by_fuzzy_name, get_genres_by_partial_name, update_genre, disable_genre, enable_genre,
    genre_name_taken, get_genre_statistics,
    get_genre_by_name_any, get_genres_by_partial_name_any, get_genres_by_fuzzy_name_any
)

router = APIRouter()


@router.get("/", response_model=List[GenreOut])
async def list_genres(
    name: Optional[str] = Query(None, description="Exact genre name to filter"),
    q: Optional[str] = Query(None, description="Partial/fuzzy name search"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """List genres with rbac: admins see all; others see active only."""
    is_admin = bool(current_user and getattr(current_user, "role", None) == "admin")

    if name:
        genre = get_genre_by_name_any(db, name) if is_admin else get_genre_by_name(db, name)
        if not genre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
        return [genre]
    if q:
        if is_admin:
            partial = get_genres_by_partial_name_any(db, q)
            if partial:
                return partial
            return get_genres_by_fuzzy_name_any(db, q)
        else:
            partial = get_genres_by_partial_name(db, q)
            if partial:
                return partial
            return get_genres_by_fuzzy_name(db, q)
    return get_all_genres(db) if is_admin else get_all_active_genres(db)


@router.get("/{genre_id}", response_model=GenreOut)
async def get_genre(genre_id: int, db: Session = Depends(get_db)):
    """Get a specific genre by ID - public access"""
    genre = get_genre_by_id(db, genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return genre


@router.post("/", response_model=GenreOut, status_code=status.HTTP_201_CREATED)
async def create_new_genre(
    genre_data: GenreCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new genre - admin only"""
    created = create_genre(db, genre_data)
    if created is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Genre name already exists")
    return created


@router.put("/{genre_id}", response_model=GenreOut)
async def update_genre_endpoint(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Update a genre - admin only"""
    if genre_data.name and genre_name_taken(db, genre_data.name, exclude_genre_id=genre_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre name already exists"
        )
    
    updated_genre = update_genre(db, genre_id, genre_data)
    if not updated_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return updated_genre


@router.patch("/{genre_id}", response_model=GenreOut)
async def partial_update_genre(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Partially update a genre - admin only"""
    if genre_data.name and genre_name_taken(db, genre_data.name, exclude_genre_id=genre_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre name already exists"
        )
    
    updated_genre = update_genre(db, genre_id, genre_data)
    if not updated_genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return updated_genre


@router.post("/{genre_id}/disable")
async def disable_genre_endpoint(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Disable a genre - admin only"""
    success = disable_genre(db, genre_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return {"message": "Genre disabled successfully"}


@router.post("/{genre_id}/enable")
async def enable_genre_endpoint(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Enable a genre - admin only"""
    success = enable_genre(db, genre_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return {"message": "Genre enabled successfully"}


@router.get("/statistics", response_model=GenreStats)
async def get_genre_statistics_endpoint(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get genre statistics"""
    stats = get_genre_statistics(db)
    return GenreStats(**stats) 

