from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
from app.db.models.playlist_song import PlaylistSong
from app.db.models.playlist import Playlist
from app.db.models.song import Song
from app.db.models.artist import Artist
from app.db.models.genre import Genre
from app.schemas.playlist_song import PlaylistSongCreate, PlaylistSongUpdate, PlaylistSongStats


def add_song_to_playlist(
    db: Session, 
    playlist_id: int, 
    song_id: int, 
    song_order: Optional[int] = None
) -> PlaylistSong:
    """
    Add a song to a playlist with optional order
    """
    # Check if song already exists in playlist
    existing_song = db.query(PlaylistSong).filter(
        and_(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
    ).first()
    
    if existing_song:
        raise ValueError("Song is already in this playlist")
    
    # Auto-calculate order if not provided
    if song_order is None:
        max_order = db.query(func.max(PlaylistSong.song_order)).filter(
            PlaylistSong.playlist_id == playlist_id
        ).scalar()
        song_order = (max_order or 0) + 1
    
    playlist_song = PlaylistSong(
        playlist_id=playlist_id,
        song_id=song_id,
        song_order=song_order
    )
    
    db.add(playlist_song)
    db.commit()
    db.refresh(playlist_song)
    return playlist_song


def get_songs_in_playlist(
    db: Session, 
    playlist_id: int, 
    skip: int = 0, 
    limit: int = 50
) -> Tuple[List[PlaylistSong], int]:
    """
    Get songs in a playlist, ordered by song_order
    """
    query = db.query(PlaylistSong).options(
        joinedload(PlaylistSong.song).joinedload(Song.artist),
        joinedload(PlaylistSong.song).joinedload(Song.band),
        joinedload(PlaylistSong.song).joinedload(Song.genre)
    ).filter(PlaylistSong.playlist_id == playlist_id)
    
    total = query.count()
    songs = query.order_by(PlaylistSong.song_order).offset(skip).limit(limit).all()
    
    return songs, total


def get_playlist_song_entry(
    db: Session, 
    playlist_id: int, 
    song_id: int
) -> Optional[PlaylistSong]:
    """
    Get a specific playlist-song entry
    """
    return db.query(PlaylistSong).filter(
        and_(
            PlaylistSong.playlist_id == playlist_id,
            PlaylistSong.song_id == song_id
        )
    ).first()


def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int) -> bool:
    """
    Remove a song from a playlist
    """
    playlist_song = get_playlist_song_entry(db, playlist_id, song_id)
    if not playlist_song:
        return False
    
    db.delete(playlist_song)
    db.commit()
    return True


def reorder_playlist_song(
    db: Session, 
    playlist_id: int, 
    song_id: int, 
    new_order: int
) -> Optional[PlaylistSong]:
    """
    Reorder a song within a playlist
    """
    playlist_song = get_playlist_song_entry(db, playlist_id, song_id)
    if not playlist_song:
        return None
    
    playlist_song.song_order = new_order
    db.commit()
    db.refresh(playlist_song)
    return playlist_song


def reorder_playlist_bulk(
    db: Session, 
    playlist_id: int, 
    song_orders: List[dict]
) -> bool:
    """
    Bulk reorder songs in a playlist
    song_orders format: [{"song_id": 1, "new_order": 3}, ...]
    """
    try:
        for order_item in song_orders:
            song_id = order_item.get("song_id")
            new_order = order_item.get("new_order")
            
            if song_id is not None and new_order is not None:
                reorder_playlist_song(db, playlist_id, song_id, new_order)
        
        return True
    except Exception:
        db.rollback()
        return False


def clear_playlist(db: Session, playlist_id: int) -> int:
    """
    Remove all songs from a playlist
    """
    result = db.query(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id
    ).delete()
    
    db.commit()
    return result


def get_playlist_song_stats(db: Session, playlist_id: int) -> PlaylistSongStats:
    """
    Get comprehensive statistics for songs in a playlist
    """
    # Basic song statistics
    song_stats = db.query(
        func.count(PlaylistSong.id).label('total_songs'),
        func.sum(Song.song_duration).label('total_duration'),
        func.avg(Song.song_duration).label('average_duration')
    ).join(Song).filter(PlaylistSong.playlist_id == playlist_id).first()
    
    # Shortest song
    shortest_song = db.query(Song).join(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id
    ).order_by(Song.song_duration).first()
    
    # Longest song
    longest_song = db.query(Song).join(PlaylistSong).filter(
        PlaylistSong.playlist_id == playlist_id
    ).order_by(desc(Song.song_duration)).first()
    
    # Most common artist
    most_common_artist = db.query(
        Artist.artist_stage_name, func.count(PlaylistSong.id).label('song_count')
    ).select_from(PlaylistSong).join(Song).join(Artist).filter(
        PlaylistSong.playlist_id == playlist_id
    ).group_by(Artist.artist_stage_name).order_by(desc('song_count')).first()
    
    # Most common genre
    most_common_genre = db.query(
        Genre.name, func.count(PlaylistSong.id).label('song_count')
    ).select_from(PlaylistSong).join(Song).join(Genre).filter(
        PlaylistSong.playlist_id == playlist_id
    ).group_by(Genre.name).order_by(desc('song_count')).first()
    
    return PlaylistSongStats(
        total_songs=song_stats.total_songs or 0,
        total_duration=song_stats.total_duration or 0,
        average_song_duration=song_stats.average_duration or 0.0,
        shortest_song=shortest_song,
        longest_song=longest_song,
        most_common_artist=most_common_artist[0] if most_common_artist else None,
        most_common_genre=most_common_genre[0] if most_common_genre else None
    )
