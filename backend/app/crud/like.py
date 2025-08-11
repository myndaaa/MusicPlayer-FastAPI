from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timezone
from fastapi import HTTPException

from app.db.models.like import Like
from app.db.models.user import User
from app.db.models.song import Song
from app.schemas.like import LikeCreate


def get_like_by_id(db: Session, like_id: int) -> Optional[Like]:
    """
    Get a like by its ID.
    Args:
        db: Database session
        like_id: ID of the like
    Returns:
        Optional[Like]: The like object if found, None otherwise
    """
    return db.query(Like).filter(Like.id == like_id).first()


def get_user_likes(
    db: Session, 
    user_id: Optional[int] = None, 
    skip: int = 0, 
    limit: int = 50
) -> List[Like]:
    """
    Get all likes by a specific user with pagination, or all likes if user_id is None.
    Args:
        db: Database session
        user_id: ID of the user (None for all likes)
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List[Like]: List of likes
    """
    query = db.query(Like)
    if user_id is not None:
        query = query.filter(Like.user_id == user_id)
    return query.order_by(desc(Like.liked_at)).offset(skip).limit(limit).all()


def get_user_likes_with_songs(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 50,
    search: Optional[str] = None
) -> List[Tuple[Like, Song]]:
    """
    Get all likes by a specific user with full song details and optional search.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term to filter songs by title
    Returns:
        List[Tuple[Like, Song]]: List of (like, song) tuples
    """
    query = db.query(Like, Song).join(Song, Like.song_id == Song.id).filter(
        Like.user_id == user_id
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Song.title.ilike(search_term)
        )
    
    return query.order_by(desc(Like.liked_at)).offset(skip).limit(limit).all()


def is_song_liked_by_user(db: Session, user_id: int, song_id: int) -> bool:
    """
    Check if a user has liked a specific song.
    Args:
        db: Database session
        user_id: ID of the user
        song_id: ID of the song
    Returns:
        bool: True if user liked the song, False otherwise
    """
    like = db.query(Like).filter(
        and_(Like.user_id == user_id, Like.song_id == song_id)
    ).first()
    return like is not None


def toggle_like(db: Session, user_id: int, song_id: int) -> Tuple[Like, bool]:
    """
    Toggle like status for a song (like if not liked, unlike if liked).
    Args:
        db: Database session
        user_id: ID of the user
        song_id: ID of the song
    Returns:
        Tuple[Like, bool]: (like object, was_created)
    """
    existing_like = db.query(Like).filter(
        and_(Like.user_id == user_id, Like.song_id == song_id)
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return existing_like, False
    else:
        # Create new like
        like_data = LikeCreate(user_id=user_id, song_id=song_id)
        db_like = Like(**like_data.model_dump())
        db_like.liked_at = datetime.now(timezone.utc)
        
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like, True


def count_song_likes(db: Session, song_id: int) -> int:
    """
    Count total likes for a song.
    Args:
        db: Database session
        song_id: ID of the song
    Returns:
        int: Number of likes for the song
    """
    return db.query(func.count(Like.id)).filter(Like.song_id == song_id).scalar()


def count_user_likes(db: Session, user_id: Optional[int] = None) -> int:
    """
    Count total likes by a user, or all likes if user_id is None.
    Args:
        db: Database session
        user_id: ID of the user (None for all likes)
    Returns:
        int: Number of likes
    """
    query = db.query(func.count(Like.id))
    if user_id is not None:
        query = query.filter(Like.user_id == user_id)
    return query.scalar()


def get_top_liked_songs(db: Session, limit: int = 10) -> List[Tuple[Song, int]]:
    """
    Get top liked songs with their like counts.
    Args:
        db: Database session
        limit: Maximum number of songs to return
    Returns:
        List[Tuple[Song, int]]: List of (song, like_count) tuples
    """
    result = db.query(
        Song, 
        func.count(Like.id).label('like_count')
    ).outerjoin(Like).group_by(Song.id).order_by(
        desc('like_count')
    ).limit(limit).all()
    
    return [(song, like_count) for song, like_count in result]


def get_like_statistics(db: Session) -> dict:
    """
    Get overall like statistics.
    Args:
        db: Database session
    Returns:
        dict: Dictionary with like statistics
    """
    total_likes = db.query(func.count(Like.id)).scalar()
    unique_songs = db.query(func.count(func.distinct(Like.song_id))).scalar()
    unique_users = db.query(func.count(func.distinct(Like.user_id))).scalar()
    
    most_liked_song = db.query(
        Song, 
        func.count(Like.id).label('like_count')
    ).join(Like).group_by(Song.id).order_by(
        desc('like_count')
    ).first()
    
    return {
        "total_likes": total_likes,
        "unique_songs": unique_songs,
        "unique_users": unique_users,
        "most_liked_song": most_liked_song[0] if most_liked_song else None,
        "most_liked_song_count": most_liked_song[1] if most_liked_song else 0
    }





def get_user_likes_summary(db: Session, user_id: int) -> dict:
    """
    Get a summary of user's likes including favorite artists and genres.
    Args:
        db: Database session
        user_id: ID of the user
    Returns:
        dict: Summary of user's likes
    """
    from app.db.models.genre import Genre
    
    liked_songs = db.query(Song).join(Like).filter(
        Like.user_id == user_id
    ).all()
    
    favorite_artists = db.query(
        Song.artist_name,
        func.count(Like.id).label('like_count')
    ).join(Like).filter(
        and_(Like.user_id == user_id, Song.artist_name.isnot(None))
    ).group_by(Song.artist_name).order_by(
        desc('like_count')
    ).limit(5).all()
    
    favorite_genres = db.query(
        Genre.name,
        func.count(Like.id).label('like_count')
    ).join(Song, Genre.id == Song.genre_id).join(Like).filter(
        Like.user_id == user_id
    ).group_by(Genre.name).order_by(
        desc('like_count')
    ).limit(5).all()
    
    return {
        "user_id": user_id,
        "total_likes": len(liked_songs),
        "liked_songs": liked_songs,
        "favorite_artists": [artist[0] for artist in favorite_artists],
        "favorite_genres": [genre[0] for genre in favorite_genres]
    }

