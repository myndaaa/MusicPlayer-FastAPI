from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.band import Band
from app.schemas.band import BandCreate, BandUpdate


def create_band(db: Session, band_data: BandCreate, created_by_user_id: int) -> Band:
    """
    Create a new band.
    Args:
        db: Database session
        band_data: Band creation data
        created_by_user_id: ID of the user creating the band
    Returns:
        Created band object
    Raises:
        ValueError: If band name already exists
    """
    if band_name_taken(db, band_data.name):
        raise ValueError("Band name already exists")
    
    band = Band(
        name=band_data.name,
        bio=band_data.bio,
        profile_picture=band_data.profile_picture,
        social_link=band_data.social_link,
        created_at=datetime.now(timezone.utc),
        created_by_user_id=created_by_user_id
    )
    
    db.add(band)
    db.commit()
    db.refresh(band)
    return band


def get_band_by_id(db: Session, band_id: int) -> Optional[Band]:
    """
    Get band by primary key.
    Args:
        db: Database session
        band_id: Band ID to retrieve
    Returns:
        Band object if found, None otherwise
    """
    return db.query(Band).filter(Band.id == band_id).first()


def get_band_by_name(db: Session, name: str) -> Optional[Band]:
    """
    Get band by name.
    Args:
        db: Database session
        name: Band name to search for
    Returns:
        Band object if found, None otherwise
    """
    return db.query(Band).filter(Band.name == name).first()


def get_all_bands(db: Session, skip: int = 0, limit: int = 10) -> List[Band]:
    """
    Get paginated list of all bands.
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List of band objects
    """
    return db.query(Band).offset(skip).limit(limit).all()


def get_all_bands_unpaginated(db: Session) -> List[Band]:
    """
    Get all bands without pagination.
    Args:
        db: Database session
    Returns:
        List of all band objects
    """
    return db.query(Band).all()


def get_active_bands(db: Session, skip: int = 0, limit: int = 10) -> List[Band]:
    """
    Get only active (non-disabled) bands.
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List of active band objects
    """
    return db.query(Band).filter(Band.is_disabled == False).offset(skip).limit(limit).all()


def update_band(db: Session, band_id: int, band_data: BandUpdate) -> Optional[Band]:
    """
    Update band information.
    Args:
        db: Database session
        band_id: Band ID to update
        band_data: Update data
    Returns:
        Updated band object if found, None otherwise
    Raises:
        ValueError: If new name conflicts with existing band
    """
    band = get_band_by_id(db, band_id)
    if not band:
        return None
    
    if band_data.name and band_data.name != band.name:
        if band_name_taken(db, band_data.name, exclude_band_id=band_id):
            raise ValueError("Band name already taken")
    
    for field, value in band_data.dict(exclude_unset=True).items():
        setattr(band, field, value)
    
    db.add(band)
    db.commit()
    db.refresh(band)
    return band


def disable_band(db: Session, band_id: int) -> bool:
    """
    Disable a band.
    Args:
        db: Database session
        band_id: Band ID to disable
    Returns:
        True if band was disabled, False if not found
    """
    band = get_band_by_id(db, band_id)
    if not band:
        return False
    
    band.is_disabled = True
    band.disabled_at = datetime.now(timezone.utc)
    db.add(band)
    db.commit()
    db.refresh(band)
    return True


def enable_band(db: Session, band_id: int) -> bool:
    """
    Enable a disabled band.
    Args:
        db: Database session
        band_id: Band ID to enable
    Returns:
        True if band was enabled, False if not found
    """
    band = get_band_by_id(db, band_id)
    if not band:
        return False
    
    band.is_disabled = False
    band.disabled_at = None
    db.add(band)
    db.commit()
    db.refresh(band)
    return True


def delete_band_permanently(db: Session, band_id: int) -> bool:
    """
    Permanently delete a band.
    Args:
        db: Database session
        band_id: Band ID to delete
    Returns:
        True if band was deleted, False if not found
    """
    band = get_band_by_id(db, band_id)
    if not band:
        return False
    
    db.delete(band)
    db.commit()
    return True


def band_exists(db: Session, band_id: int) -> bool:
    """
    Check if band exists.
    Args:
        db: Database session
        band_id: Band ID to check
    Returns:
        True if band exists, False otherwise
    """
    return db.query(Band).filter(Band.id == band_id).first() is not None


def band_name_taken(db: Session, name: str, exclude_band_id: Optional[int] = None) -> bool:
    """
    Check if band name is already taken.
    Args:
        db: Database session
        name: Band name to check
        exclude_band_id: Band ID to exclude from check (for updates)
    Returns:
        True if name is taken, False otherwise
    """
    query = db.query(Band).filter(Band.name == name)
    if exclude_band_id:
        query = query.filter(Band.id != exclude_band_id)
    return query.first() is not None


def get_band_with_related_entities(db: Session, band_id: int) -> Optional[Band]:
    """
    Get band with related entities (songs, albums, members).
    Args:
        db: Database session
        band_id: Band ID to retrieve
    Returns:
        Band object with related entities if found, None otherwise
    """
    return db.query(Band).filter(Band.id == band_id).first()


def search_bands_by_name(db: Session, keyword: str, skip: int = 0, limit: int = 10) -> List[Band]:
    """
    Search bands by name using case-insensitive partial match.
    Args:
        db: Database session
        keyword: Search keyword
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List of matching band objects
    """
    return db.query(Band).filter(
        Band.name.ilike(f"%{keyword}%")
    ).offset(skip).limit(limit).all()


def get_band_statistics(db: Session) -> dict:
    """
    Get band statistics.
    Args:
        db: Database session
    Returns:
        Dictionary with band statistics
    """
    total_bands = db.query(Band).count()
    active_bands = db.query(Band).filter(Band.is_disabled == False).count()
    disabled_bands = db.query(Band).filter(Band.is_disabled == True).count()
    
    return {
        "total_bands": total_bands,
        "active_bands": active_bands,
        "disabled_bands": disabled_bands
    }


def is_band_owner(db: Session, band_id: int, user_id: int) -> bool:
    """Check if a user is the owner of a band"""
    band = db.query(Band).filter(Band.id == band_id).first()
    if not band:
        return False
    return band.created_by_user_id == user_id
