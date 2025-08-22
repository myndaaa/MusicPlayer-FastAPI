from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.schemas.genre import GenreCreate, GenreUpdate, GenreOut, GenreStats
from app.crud.genre import (
    create_genre, get_genre_by_id, get_genre_by_name, get_all_genres,
    get_all_active_genres, update_genre, disable_genre, enable_genre,
    genre_exists, genre_name_taken, get_genre_statistics
)

router = APIRouter()


@router.get("/", response_model=List[GenreOut])
async def get_active_genres(db: Session = Depends(get_db)):
    """Get all active genres - public access"""
    return get_all_active_genres(db)


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


@router.get("/name/{name}", response_model=GenreOut)
async def get_genre_by_name_endpoint(name: str, db: Session = Depends(get_db)):
    """Get a specific genre by name - public access"""
    genre = get_genre_by_name(db, name)
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
    if genre_name_taken(db, genre_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre name already exists"
        )
    
    return create_genre(db, genre_data)


@router.put("/{genre_id}", response_model=GenreOut)
async def update_genre_endpoint(
    genre_id: int,
    genre_data: GenreUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Update a genre - admin only"""
    if not genre_exists(db, genre_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
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
    if not genre_exists(db, genre_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
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


@router.delete("/{genre_id}")
async def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a genre - admin only"""
    if not genre_exists(db, genre_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    success = disable_genre(db, genre_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return {"message": "Genre disabled successfully"}


@router.post("/{genre_id}/disable")
async def disable_genre_endpoint(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Disable a genre - admin only"""
    if not genre_exists(db, genre_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    success = disable_genre(db, genre_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return {"message": "Genre disabled successfully"}


@router.post("/{genre_id}/enable")
async def enable_genre_endpoint(
    genre_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Enable a genre - admin only"""
    if not genre_exists(db, genre_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    success = enable_genre(db, genre_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    
    return {"message": "Genre enabled successfully"}


@router.get("/admin/all", response_model=List[GenreOut])
async def get_all_genres_admin(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get all genres including inactive ones - admin only"""
    return get_all_genres(db)


@router.get("/admin/statistics", response_model=GenreStats)
async def get_genre_statistics_endpoint(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """Get genre statistics - admin only"""
    stats = get_genre_statistics(db)
    return GenreStats(**stats) 
