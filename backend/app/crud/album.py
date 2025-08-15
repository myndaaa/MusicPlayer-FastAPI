"""
CRUD operations for Album model.
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.db.models.album import Album
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.schemas.album import AlbumCreate, AlbumUpdate


def create_album(db: Session, album_data: AlbumCreate, uploaded_by_user_id: int) -> Album:
    """
    Create a new album.
    
    Args:
        db: Database session
        album_data: Album creation data
        uploaded_by_user_id: ID of the user uploading the album
        
    Returns:
        Created album object
        
    Raises:
        ValueError: If artist_id or band_id doesn't exist
    """
    if album_data.album_artist_id:
        artist = db.query(Artist).filter(Artist.id == album_data.album_artist_id).first()
        if not artist:
            raise ValueError("Artist not found")
    
    if album_data.album_band_id:
        band = db.query(Band).filter(Band.id == album_data.album_band_id).first()
        if not band:
            raise ValueError("Band not found")
    
    album = Album(
        title=album_data.title,
        description=album_data.description,
        cover_image=album_data.cover_image,
        release_date=album_data.release_date,
        uploaded_by_user_id=uploaded_by_user_id,
        album_artist_id=album_data.album_artist_id,
        album_band_id=album_data.album_band_id,
        artist_name=album_data.artist_name,
        band_name=album_data.band_name
    )
    
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


def get_album_by_id(db: Session, album_id: int) -> Optional[Album]:
    """
    Get album by primary key.
    
    Args:
        db: Database session
        album_id: Album ID to retrieve
        
    Returns:
        Album object if found, None otherwise
    """
    return db.query(Album).filter(Album.id == album_id).first()


def get_albums_by_artist(db: Session, artist_id: int, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Get albums by artist ID.
    
    Args:
        db: Database session
        artist_id: Artist ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album objects
    """
    return db.query(Album).filter(Album.album_artist_id == artist_id).offset(skip).limit(limit).all()


def get_albums_by_band(db: Session, band_id: int, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Get albums by band ID.
    
    Args:
        db: Database session
        band_id: Band ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album objects
    """
    return db.query(Album).filter(Album.album_band_id == band_id).offset(skip).limit(limit).all()


def get_albums_by_title(db: Session, title: str, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Search albums by title (case-insensitive).
    
    Args:
        db: Database session
        title: Title to search for
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching album objects
    """
    return db.query(Album).filter(Album.title.ilike(f"%{title}%")).offset(skip).limit(limit).all()


def get_all_albums(db: Session, skip: int = 0, limit: int = 50) -> List[Album]:
    """
    Get paginated list of all albums.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album objects
    """
    return db.query(Album).offset(skip).limit(limit).all()


def update_album(db: Session, album_id: int, album_data: AlbumUpdate) -> Optional[Album]:
    """
    Update album information.
    
    Args:
        db: Database session
        album_id: Album ID to update
        album_data: Update data
        
    Returns:
        Updated album object if found, None otherwise
    """
    album = get_album_by_id(db, album_id)
    if not album:
        return None
    
    for field, value in album_data.dict(exclude_unset=True).items():
        setattr(album, field, value)
    
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


def get_album_with_songs(db: Session, album_id: int) -> Optional[Album]:
    """
    Get album with eager-loaded songs, artist, and band.
    
    Args:
        db: Database session
        album_id: Album ID to retrieve
        
    Returns:
        Album object with loaded relationships if found, None otherwise
    """
    return db.query(Album).options(
        joinedload(Album.album_songs),
        joinedload(Album.artist),
        joinedload(Album.band)
    ).filter(Album.id == album_id).first()


def get_albums_released_between(
    db: Session, 
    start_date: datetime, 
    end_date: datetime, 
    skip: int = 0, 
    limit: int = 20
) -> List[Album]:
    """
    Get albums released between two dates.
    
    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album objects
    """
    return db.query(Album).filter(
        Album.release_date >= start_date,
        Album.release_date <= end_date
    ).offset(skip).limit(limit).all()


def get_albums_by_artist_name(db: Session, artist_name: str, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Get albums by artist name (case-insensitive).
    
    Args:
        db: Database session
        artist_name: Artist name to search for
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching album objects
    """
    return db.query(Album).filter(Album.artist_name.ilike(f"%{artist_name}%")).offset(skip).limit(limit).all()


def get_albums_by_band_name(db: Session, band_name: str, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Get albums by band name (case-insensitive).
    
    Args:
        db: Database session
        band_name: Band name to search for
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of matching album objects
    """
    return db.query(Album).filter(Album.band_name.ilike(f"%{band_name}%")).offset(skip).limit(limit).all()


def album_exists(db: Session, album_id: int) -> bool:
    """
    Check if album exists.
    
    Args:
        db: Database session
        album_id: Album ID to check
        
    Returns:
        True if album exists, False otherwise
    """
    return db.query(Album).filter(Album.id == album_id).first() is not None


def validate_artist_exists(db: Session, artist_id: int) -> bool:
    """
    Validate that artist exists.
    
    Args:
        db: Database session
        artist_id: Artist ID to validate
        
    Returns:
        True if artist exists, False otherwise
    """
    return db.query(Artist).filter(Artist.id == artist_id).first() is not None


def validate_band_exists(db: Session, band_id: int) -> bool:
    """
    Validate that band exists.
    
    Args:
        db: Database session
        band_id: Band ID to validate
        
    Returns:
        True if band exists, False otherwise
    """
    return db.query(Band).filter(Band.id == band_id).first() is not None


def get_album_count(db: Session) -> int:
    """
    Get total number of albums.
    
    Args:
        db: Database session
        
    Returns:
        Total count of albums
    """
    return db.query(func.count(Album.id)).scalar()


def get_albums_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[Album]:
    """
    Get albums uploaded by a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album objects
    """
    return db.query(Album).filter(Album.uploaded_by_user_id == user_id).offset(skip).limit(limit).all()
