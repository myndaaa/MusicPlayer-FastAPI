from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timezone
from fastapi import HTTPException

from app.db.models.following import Following
from app.db.models.user import User
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.schemas.following import FollowingCreate


def get_following_by_id(db: Session, following_id: int) -> Optional[Following]:
    """
    Get a following by its ID.
    Args:
        db: Database session
        following_id: ID of the following
    Returns:
        Optional[Following]: The following object if found, None otherwise
    """
    return db.query(Following).filter(Following.id == following_id).first()


def get_following_by_user_and_target(
    db: Session, user_id: int, artist_id: Optional[int] = None, band_id: Optional[int] = None
) -> Optional[Following]:
    """
    Get a following by user ID and target (artist or band).
    Args:
        db: Database session
        user_id: ID of the user
        artist_id: ID of the artist (optional)
        band_id: ID of the band (optional)
    Returns:
        Optional[Following]: The following object if found, None otherwise
    """
    query = db.query(Following).filter(Following.user_id == user_id)
    
    if artist_id is not None:
        query = query.filter(Following.artist_id == artist_id)
    elif band_id is not None:
        query = query.filter(Following.band_id == band_id)
    
    return query.first()


def create_following(
    db: Session, user_id: int, artist_id: Optional[int] = None, band_id: Optional[int] = None
) -> Following:
    """
    Create a new following relationship.
    Args:
        db: Database session
        user_id: ID of the user
        artist_id: ID of the artist (optional)
        band_id: ID of the band (optional)
    Returns:
        Following: The created following object
    """
    following_data = FollowingCreate(
        user_id=user_id, 
        artist_id=artist_id, 
        band_id=band_id
    )
    db_following = Following(**following_data.model_dump())
    db_following.started_at = datetime.now(timezone.utc)
    
    db.add(db_following)
    db.commit()
    db.refresh(db_following)
    return db_following


def delete_following(
    db: Session, user_id: int, artist_id: Optional[int] = None, band_id: Optional[int] = None
) -> bool:
    """
    Delete a following relationship.
    Args:
        db: Database session
        user_id: ID of the user
        artist_id: ID of the artist (optional)
        band_id: ID of the band (optional)
    Returns:
        bool: True if deleted, False if not found
    """
    following = get_following_by_user_and_target(db, user_id, artist_id, band_id)
    if following:
        db.delete(following)
        db.commit()
        return True
    return False


def toggle_following(
    db: Session, user_id: int, artist_id: Optional[int] = None, band_id: Optional[int] = None
) -> Tuple[Following, bool]:
    """
    Toggle following status (follow if not following, unfollow if following).
    Args:
        db: Database session
        user_id: ID of the user
        artist_id: ID of the artist (optional)
        band_id: ID of the band (optional)
    Returns:
        Tuple[Following, bool]: (following object, was_created)
    """
    existing_following = get_following_by_user_and_target(db, user_id, artist_id, band_id)
    
    if existing_following:
        db.delete(existing_following)
        db.commit()
        return existing_following, False
    else:
        new_following = create_following(db, user_id, artist_id, band_id)
        return new_following, True


def get_user_followings(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> List[Following]:
    """
    Get all followings by a specific user with pagination.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List[Following]: List of followings by the user
    """
    return db.query(Following).filter(
        Following.user_id == user_id
    ).order_by(desc(Following.started_at)).offset(skip).limit(limit).all()


def get_user_followings_with_targets(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> List[Tuple[Following, Optional[Artist], Optional[Band]]]:
    """
    Get all followings by a user with target details (artist or band).
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List[Tuple[Following, Optional[Artist], Optional[Band]]]: List of (following, artist, band) tuples
    """
    return db.query(Following, Artist, Band).outerjoin(
        Artist, Following.artist_id == Artist.id
    ).outerjoin(
        Band, Following.band_id == Band.id
    ).filter(
        Following.user_id == user_id
    ).order_by(desc(Following.started_at)).offset(skip).limit(limit).all()


def is_user_following_artist(db: Session, user_id: int, artist_id: int) -> bool:
    """
    Check if a user is following a specific artist.
    Args:
        db: Database session
        user_id: ID of the user
        artist_id: ID of the artist
    Returns:
        bool: True if user is following the artist, False otherwise
    """
    following = db.query(Following).filter(
        and_(Following.user_id == user_id, Following.artist_id == artist_id)
    ).first()
    return following is not None


def is_user_following_band(db: Session, user_id: int, band_id: int) -> bool:
    """
    Check if a user is following a specific band.
    Args:
        db: Database session
        user_id: ID of the user
        band_id: ID of the band
    Returns:
        bool: True if user is following the band, False otherwise
    """
    following = db.query(Following).filter(
        and_(Following.user_id == user_id, Following.band_id == band_id)
    ).first()
    return following is not None


def count_artist_followers(db: Session, artist_id: int) -> int:
    """
    Count total followers for an artist.
    Args:
        db: Database session
        artist_id: ID of the artist
    Returns:
        int: Number of followers for the artist
    """
    return db.query(func.count(Following.id)).filter(Following.artist_id == artist_id).scalar()


def count_band_followers(db: Session, band_id: int) -> int:
    """
    Count total followers for a band.
    Args:
        db: Database session
        band_id: ID of the band
    Returns:
        int: Number of followers for the band
    """
    return db.query(func.count(Following.id)).filter(Following.band_id == band_id).scalar()


def count_user_followings(db: Session, user_id: int) -> int:
    """
    Count total followings by a user.
    Args:
        db: Database session
        user_id: ID of the user
    Returns:
        int: Number of followings by the user
    """
    return db.query(func.count(Following.id)).filter(Following.user_id == user_id).scalar()


def get_following_statistics(db: Session) -> dict:
    """
    Get overall following statistics.
    Args:
        db: Database session
    Returns:
        dict: Dictionary with following statistics
    """
    total_followings = db.query(func.count(Following.id)).scalar()
    unique_users = db.query(func.count(func.distinct(Following.user_id))).scalar()
    unique_artists = db.query(func.count(func.distinct(Following.artist_id))).scalar()
    unique_bands = db.query(func.count(func.distinct(Following.band_id))).scalar()
    
    most_followed_artist = db.query(
        Artist, 
        func.count(Following.id).label('follower_count')
    ).join(Following).group_by(Artist.id).order_by(
        desc('follower_count')
    ).first()
    
    most_followed_band = db.query(
        Band, 
        func.count(Following.id).label('follower_count')
    ).join(Following).group_by(Band.id).order_by(
        desc('follower_count')
    ).first()
    
    return {
        "total_followings": total_followings,
        "unique_users": unique_users,
        "unique_artists": unique_artists,
        "unique_bands": unique_bands,
        "most_followed_artist": most_followed_artist[0] if most_followed_artist else None,
        "most_followed_band": most_followed_band[0] if most_followed_band else None
    }


def get_user_following_summary(db: Session, user_id: int) -> dict:
    """
    Get a summary of user's followings including counts and lists.
    Args:
        db: Database session
        user_id: ID of the user
    Returns:
        dict: Summary of user's followings
    """
    followings_with_targets = get_user_followings_with_targets(db, user_id, skip=0, limit=1000)
    
    followed_artists = []
    followed_bands = []
    
    for following, artist, band in followings_with_targets:
        if artist:
            followed_artists.append(artist)
        if band:
            followed_bands.append(band)
    
    return {
        "user_id": user_id,
        "total_following": len(followings_with_targets),
        "artist_count": len(followed_artists),
        "band_count": len(followed_bands),
        "followed_artists": followed_artists,
        "followed_bands": followed_bands
    }
