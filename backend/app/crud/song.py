from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.db.models.song import Song
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.db.models.genre import Genre
from app.db.models.user import User
from app.schemas.song import SongUploadByArtist, SongUploadByBand, SongUploadByAdmin, SongUpdate


def create_song_by_artist(db: Session, song_data: SongUploadByArtist, uploaded_by_user_id: int) -> Song:
    """Create a song uploaded by an artist"""
    # Auto-fill artist_name from artist_id
    artist = db.query(Artist).filter(Artist.id == song_data.artist_id).first()
    if not artist:
        raise ValueError("Artist not found")
    
    db_song = Song(
        title=song_data.title,
        genre_id=song_data.genre_id,
        artist_id=song_data.artist_id,
        band_id=None,
        release_date=song_data.release_date,
        song_duration=song_data.song_duration,
        file_path=song_data.file_path,
        cover_image=song_data.cover_image,
        artist_name=artist.artist_stage_name,
        band_name=None,
        uploaded_by_user_id=uploaded_by_user_id
    )
    
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def create_song_by_band(db: Session, song_data: SongUploadByBand, uploaded_by_user_id: int) -> Song:
    """Create a song uploaded by a band member"""
    # Auto-fill band_name from band_id
    band = db.query(Band).filter(Band.id == song_data.band_id).first()
    if not band:
        raise ValueError("Band not found")
    
    db_song = Song(
        title=song_data.title,
        genre_id=song_data.genre_id,
        artist_id=None,
        band_id=song_data.band_id,
        release_date=song_data.release_date,
        song_duration=song_data.song_duration,
        file_path=song_data.file_path,
        cover_image=song_data.cover_image,
        artist_name=None,
        band_name=band.name,
        uploaded_by_user_id=uploaded_by_user_id
    )
    
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def create_song_by_admin(db: Session, song_data: SongUploadByAdmin, uploaded_by_user_id: int) -> Song:
    """Create a song uploaded by admin (for any artist/band including dead artists)"""
    db_song = Song(
        title=song_data.title,
        genre_id=song_data.genre_id,
        artist_id=song_data.artist_id,
        band_id=song_data.band_id,
        release_date=song_data.release_date,
        song_duration=song_data.song_duration,
        file_path=song_data.file_path,
        cover_image=song_data.cover_image,
        artist_name=song_data.artist_name,
        band_name=song_data.band_name,
        uploaded_by_user_id=uploaded_by_user_id
    )
    
    if song_data.artist_id:
        artist = db.query(Artist).filter(Artist.id == song_data.artist_id).first()
        if artist:
            db_song.artist_name = artist.artist_stage_name
    
    if song_data.band_id:
        band = db.query(Band).filter(Band.id == song_data.band_id).first()
        if band:
            db_song.band_name = band.name
    
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_song_by_id(db: Session, song_id: int) -> Optional[Song]:
    """Get a song by its ID"""
    return db.query(Song).filter(Song.id == song_id).first()


def get_all_songs_paginated(db: Session, skip: int = 0, limit: int = 20) -> List[Song]:
    """Get all songs with pagination"""
    return db.query(Song).filter(Song.is_disabled == False).offset(skip).limit(limit).all()


def search_songs(db: Session, query: str, skip: int = 0, limit: int = 20) -> List[Song]:
    """Search songs by title, artist name, or band name"""
    return db.query(Song).filter(
        Song.is_disabled == False,
        (
            Song.title.ilike(f"%{query}%") |
            Song.artist_name.ilike(f"%{query}%") |
            Song.band_name.ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit).all()


def get_songs_by_artist(db: Session, artist_id: int, skip: int = 0, limit: int = 20) -> List[Song]:
    """Get songs by artist ID"""
    return db.query(Song).filter(
        Song.artist_id == artist_id,
        Song.is_disabled == False
    ).offset(skip).limit(limit).all()


def get_songs_by_band(db: Session, band_id: int, skip: int = 0, limit: int = 20) -> List[Song]:
    """Get songs by band ID"""
    return db.query(Song).filter(
        Song.band_id == band_id,
        Song.is_disabled == False
    ).offset(skip).limit(limit).all()


def get_songs_by_genre(db: Session, genre_id: int, skip: int = 0, limit: int = 20) -> List[Song]:
    """Get songs by genre ID"""
    return db.query(Song).filter(
        Song.genre_id == genre_id,
        Song.is_disabled == False
    ).offset(skip).limit(limit).all()


def update_song_file_path(db: Session, song_id: int, new_file_path: str) -> Optional[Song]:
    """Update song file path (admin only)"""
    db_song = get_song_by_id(db, song_id)
    if not db_song:
        return None
    
    db_song.file_path = new_file_path
    db.commit()
    db.refresh(db_song)
    return db_song


def update_song_metadata(db: Session, song_id: int, song_data: SongUpdate) -> Optional[Song]:
    """Update song metadata (admin only)"""
    db_song = get_song_by_id(db, song_id)
    if not db_song:
        return None
    
    update_data = song_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_song, field, value)
    
    db.commit()
    db.refresh(db_song)
    return db_song


def disable_song(db: Session, song_id: int) -> bool:
    """Disable a song (soft delete)"""
    db_song = get_song_by_id(db, song_id)
    if not db_song:
        return False
    
    db_song.is_disabled = True
    db_song.disabled_at = datetime.now(timezone.utc)
    db.commit()
    return True


def enable_song(db: Session, song_id: int) -> bool:
    """Enable a song (re-enable)"""
    db_song = get_song_by_id(db, song_id)
    if not db_song:
        return False
    
    db_song.is_disabled = False
    db_song.disabled_at = None
    db.commit()
    return True


def song_exists(db: Session, song_id: int) -> bool:
    """Check if a song exists by ID"""
    return db.query(Song).filter(Song.id == song_id).first() is not None


def can_user_upload_for_band(db: Session, user_id: int, band_id: int) -> bool:
    """Check if user can upload songs for a band (must be band member)"""
    from app.crud.artist_band_member import is_current_member
    return is_current_member(db, user_id, band_id)


def get_song_statistics(db: Session) -> Dict[str, Any]:
    """Get comprehensive statistics about songs"""
    total_songs = db.query(Song).count()
    active_songs = db.query(Song).filter(Song.is_disabled == False).count()
    disabled_songs = total_songs - active_songs
    
    songs_by_artist = db.query(Song).filter(
        Song.artist_id.isnot(None),
        Song.is_disabled == False
    ).count()
    
    songs_by_band = db.query(Song).filter(
        Song.band_id.isnot(None),
        Song.is_disabled == False
    ).count()
    
    # Find most uploaded artist
    most_uploaded_artist = db.query(
        Song.artist_name,
        func.count(Song.id).label('song_count')
    ).filter(
        Song.artist_id.isnot(None),
        Song.is_disabled == False
    ).group_by(Song.artist_name).order_by(func.count(Song.id).desc()).first()
    
    # Find most uploaded band
    most_uploaded_band = db.query(
        Song.band_name,
        func.count(Song.id).label('song_count')
    ).filter(
        Song.band_id.isnot(None),
        Song.is_disabled == False
    ).group_by(Song.band_name).order_by(func.count(Song.id).desc()).first()
    
    return {
        "total_songs": total_songs,
        "active_songs": active_songs,
        "disabled_songs": disabled_songs,
        "songs_by_artist": songs_by_artist,
        "songs_by_band": songs_by_band,
        "most_uploaded_artist": most_uploaded_artist.artist_name if most_uploaded_artist else None,
        "most_uploaded_band": most_uploaded_band.band_name if most_uploaded_band else None
    }

