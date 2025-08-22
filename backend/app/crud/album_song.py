"""
CRUD operations for AlbumSong model.
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.album_song import AlbumSong
from app.db.models.album import Album
from app.db.models.song import Song
from app.schemas.album_song import AlbumSongCreate, AlbumSongUpdate


def create_album_song(db: Session, album_song_data: AlbumSongCreate) -> AlbumSong:
    """
    Create a new album-song relationship.
    
    Args:
        db: Database session
        album_song_data: Album-song creation data
        
    Returns:
        Created album-song object
        
    Raises:
        ValueError: If album_id or song_id doesn't exist, or track_number is taken
    """
    album = db.query(Album).filter(Album.id == album_song_data.album_id).first()
    if not album:
        raise ValueError("Album not found")
    
    song = db.query(Song).filter(Song.id == album_song_data.song_id).first()
    if not song:
        raise ValueError("Song not found")
    
    if is_track_number_taken(db, album_song_data.album_id, album_song_data.track_number):
        raise ValueError("Track number already exists for this album")
    
    album_song = AlbumSong(
        album_id=album_song_data.album_id,
        song_id=album_song_data.song_id,
        track_number=album_song_data.track_number
    )
    
    db.add(album_song)
    db.commit()
    db.refresh(album_song)
    return album_song


def get_album_song_by_id(db: Session, album_song_id: int) -> Optional[AlbumSong]:
    """
    Get album-song relationship by primary key.
    
    Args:
        db: Database session
        album_song_id: Album-song ID to retrieve
        
    Returns:
        AlbumSong object if found, None otherwise
    """
    return db.query(AlbumSong).filter(AlbumSong.id == album_song_id).first()


def get_album_songs_by_album(db: Session, album_id: int, skip: int = 0, limit: int = 50) -> List[AlbumSong]:
    """
    Get all songs for a specific album, ordered by track number.
    
    Args:
        db: Database session
        album_id: Album ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album-song objects
    """
    return db.query(AlbumSong).filter(
        AlbumSong.album_id == album_id
    ).order_by(AlbumSong.track_number).offset(skip).limit(limit).all()


def get_album_songs_by_song(db: Session, song_id: int, skip: int = 0, limit: int = 20) -> List[AlbumSong]:
    """
    Get all albums that contain a specific song.
    
    Args:
        db: Database session
        song_id: Song ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of album-song objects
    """
    return db.query(AlbumSong).filter(
        AlbumSong.song_id == song_id
    ).order_by(AlbumSong.track_number).offset(skip).limit(limit).all()


def update_album_song(db: Session, album_song_id: int, album_song_data: AlbumSongUpdate) -> Optional[AlbumSong]:
    """
    Update album-song relationship (track number).
    
    Args:
        db: Database session
        album_song_id: Album-song ID to update
        album_song_data: Update data
        
    Returns:
        Updated album-song object if found, None otherwise
        
    Raises:
        ValueError: If new track number is already taken
    """
    album_song = get_album_song_by_id(db, album_song_id)
    if not album_song:
        return None

    if is_track_number_taken(db, album_song.album_id, album_song_data.track_number, exclude_id=album_song_id):
        raise ValueError("Track number already exists for this album")
    
    album_song.track_number = album_song_data.track_number
    db.add(album_song)
    db.commit()
    db.refresh(album_song)
    return album_song


def delete_album_song(db: Session, album_song_id: int) -> bool:
    """
    Delete album-song relationship.
    
    Args:
        db: Database session
        album_song_id: Album-song ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    album_song = get_album_song_by_id(db, album_song_id)
    if not album_song:
        return False
    
    db.delete(album_song)
    db.commit()
    return True


def delete_album_song_by_album_and_song(db: Session, album_id: int, song_id: int) -> bool:
    """
    Delete album-song relationship by album and song IDs.
    
    Args:
        db: Database session
        album_id: Album ID
        song_id: Song ID
        
    Returns:
        True if deleted, False if not found
    """
    album_song = db.query(AlbumSong).filter(
        AlbumSong.album_id == album_id,
        AlbumSong.song_id == song_id
    ).first()
    
    if not album_song:
        return False
    
    db.delete(album_song)
    db.commit()
    return True


def album_song_exists(db: Session, album_song_id: int) -> bool:
    """
    Check if album-song relationship exists.
    
    Args:
        db: Database session
        album_song_id: Album-song ID to check
        
    Returns:
        True if exists, False otherwise
    """
    return db.query(AlbumSong).filter(AlbumSong.id == album_song_id).first() is not None


def is_track_number_taken(db: Session, album_id: int, track_number: int, exclude_id: Optional[int] = None) -> bool:
    """
    Check if track number is already taken for an album.
    
    Args:
        db: Database session
        album_id: Album ID
        track_number: Track number to check
        exclude_id: Album-song ID to exclude from check (for updates)
        
    Returns:
        True if track number is taken, False otherwise
    """
    query = db.query(AlbumSong).filter(
        AlbumSong.album_id == album_id,
        AlbumSong.track_number == track_number
    )
    
    if exclude_id:
        query = query.filter(AlbumSong.id != exclude_id)
    
    return query.first() is not None


def get_album_song_count(db: Session, album_id: int) -> int:
    """
    Get total number of songs in an album.
    
    Args:
        db: Database session
        album_id: Album ID
        
    Returns:
        Total count of songs in album
    """
    return db.query(func.count(AlbumSong.id)).filter(AlbumSong.album_id == album_id).scalar()


def get_album_total_duration(db: Session, album_id: int) -> int:
    """
    Get total duration of all songs in an album.
    
    Args:
        db: Database session
        album_id: Album ID
        
    Returns:
        Total duration in seconds
    """
    result = db.query(func.sum(Song.song_duration)).join(
        AlbumSong, Song.id == AlbumSong.song_id
    ).filter(AlbumSong.album_id == album_id).scalar()
    
    return result or 0


def get_album_song_statistics(db: Session, album_id: int) -> dict:
    """
    Get comprehensive statistics for an album.
    
    Args:
        db: Database session
        album_id: Album ID
        
    Returns:
        Dictionary with album statistics
    """
    total_tracks = get_album_song_count(db, album_id)
    total_duration = get_album_total_duration(db, album_id)
    
    shortest_track = db.query(Song).join(
        AlbumSong, Song.id == AlbumSong.song_id
    ).filter(AlbumSong.album_id == album_id).order_by(Song.song_duration.asc()).first()
    
    longest_track = db.query(Song).join(
        AlbumSong, Song.id == AlbumSong.song_id
    ).filter(AlbumSong.album_id == album_id).order_by(Song.song_duration.desc()).first()
    
    average_duration = total_duration / total_tracks if total_tracks > 0 else 0
    
    return {
        "album_id": album_id,
        "total_tracks": total_tracks,
        "total_duration": total_duration,
        "average_track_duration": round(average_duration, 2),
        "shortest_track": shortest_track,
        "longest_track": longest_track
    }


def reorder_album_tracks(db: Session, album_id: int, track_orders: List[dict]) -> bool:
    """
    Bulk reorder tracks in an album.
    
    Args:
        db: Database session
        album_id: Album ID
        track_orders: List of dicts with song_id and new track_number
        
    Returns:
        True if successful, False otherwise
    """
    try:
        for track_order in track_orders:
            song_id = track_order["song_id"]
            new_track_number = track_order["track_number"]
            
            album_song = db.query(AlbumSong).filter(
                AlbumSong.album_id == album_id,
                AlbumSong.song_id == song_id
            ).first()
            
            if album_song:
                if is_track_number_taken(db, album_id, new_track_number, exclude_id=album_song.id):
                    raise ValueError(f"Track number {new_track_number} already exists")
                
                album_song.track_number = new_track_number
                db.add(album_song)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to reorder tracks: {str(e)}")

