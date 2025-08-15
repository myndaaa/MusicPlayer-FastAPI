from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.db.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreUpdate


def create_genre(db: Session, genre_data: GenreCreate) -> Genre:
    """Create a new genre in the database"""
    db_genre = Genre(
        name=genre_data.name,
        description=genre_data.description,
        is_active=True
    )
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre


def get_genre_by_id(db: Session, genre_id: int) -> Optional[Genre]:
    """Get a genre by its ID"""
    return db.query(Genre).filter(Genre.id == genre_id).first()


def get_genre_by_name(db: Session, name: str) -> Optional[Genre]:
    """Get a genre by its name"""
    return db.query(Genre).filter(Genre.name == name).first()


def get_all_genres(db: Session) -> List[Genre]:
    """Get all genres (active and inactive)"""
    return db.query(Genre).all()


def get_all_active_genres(db: Session) -> List[Genre]:
    """Get all active genres only"""
    return db.query(Genre).filter(Genre.is_active == True).all()


def update_genre(db: Session, genre_id: int, genre_data: GenreUpdate) -> Optional[Genre]:
    """Update a genre with new data"""
    db_genre = get_genre_by_id(db, genre_id)
    if not db_genre:
        return None
    
    update_data = genre_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_genre, field, value)
    
    db.commit()
    db.refresh(db_genre)
    return db_genre


def disable_genre(db: Session, genre_id: int) -> bool:
    """Disable a genre by setting is_active to False"""
    db_genre = get_genre_by_id(db, genre_id)
    if not db_genre:
        return False
    
    db_genre.is_active = False
    db_genre.disabled_at = datetime.now(timezone.utc)
    db.commit()
    return True


def enable_genre(db: Session, genre_id: int) -> bool:
    """Enable a genre by setting is_active to True"""
    db_genre = get_genre_by_id(db, genre_id)
    if not db_genre:
        return False
    
    db_genre.is_active = True
    db_genre.disabled_at = None
    db.commit()
    return True


def genre_exists(db: Session, genre_id: int) -> bool:
    """Check if a genre exists by ID"""
    return db.query(Genre).filter(Genre.id == genre_id).first() is not None


def genre_name_taken(db: Session, name: str, exclude_genre_id: Optional[int] = None) -> bool:
    """Check if a genre name is already taken"""
    query = db.query(Genre).filter(Genre.name == name)
    if exclude_genre_id:
        query = query.filter(Genre.id != exclude_genre_id)
    return query.first() is not None


def get_genre_statistics(db: Session) -> dict:
    """Get comprehensive statistics about genres"""
    total_genres = db.query(Genre).count()
    active_genres = db.query(Genre).filter(Genre.is_active == True).count()
    inactive_genres = total_genres - active_genres
    
    genres_with_songs = db.query(Genre).join(Genre.songs).distinct().count()
    
    genre_usage = db.query(
        Genre.name,
        func.count(Genre.songs).label('song_count')
    ).outerjoin(Genre.songs).group_by(Genre.name).all()
    
    most_used = None
    least_used = None
    
    if genre_usage:
        sorted_usage = sorted(genre_usage, key=lambda x: x.song_count, reverse=True)
        most_used = sorted_usage[0].name if sorted_usage[0].song_count > 0 else None
        least_used = sorted_usage[-1].name if sorted_usage[-1].song_count > 0 else None
    
    return {
        "total_genres": total_genres,
        "active_genres": active_genres,
        "inactive_genres": inactive_genres,
        "genres_with_songs": genres_with_songs,
        "most_used_genre": most_used,
        "least_used_genre": least_used
    }
