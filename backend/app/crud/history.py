from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
from app.db.models.history import History
from app.db.models.song import Song
from app.db.models.user import User
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.db.models.genre import Genre
from app.schemas.history import HistoryCreate, HistoryStats, GlobalHistoryStats


def create_history_entry(db: Session, user_id: int, song_id: int) -> Optional[History]:
    """
    Create a history entry with spam prevention (120-second cooldown for same song)
    """
    # no spam
    recent_play = db.query(History).filter(
        and_(
            History.user_id == user_id,
            History.song_id == song_id,
            History.played_at >= datetime.now(timezone.utc) - timedelta(seconds=120)
        )
    ).first()
    if recent_play:
        return None  
    
    history_entry = History(
        user_id=user_id,
        song_id=song_id,
        played_at=datetime.now(timezone.utc),
        is_cleared=False
    )
    
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry


def get_user_history(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 50,
    include_cleared: bool = False
) -> Tuple[List[History], int]:
    """
    Get user's listening history with song details, paginated
    """
    query = db.query(History).options(
        joinedload(History.song).joinedload(Song.artist),
        joinedload(History.song).joinedload(Song.band),
        joinedload(History.song).joinedload(Song.genre)
    ).filter(History.user_id == user_id)
    
    if not include_cleared:
        query = query.filter(History.is_cleared == False)
    
    total = query.count()
    history = query.order_by(desc(History.played_at)).offset(skip).limit(limit).all()
    
    return history, total


def clear_user_history(db: Session, user_id: int) -> int:
    """
    Mark all user's history entries as cleared (soft delete for analytics)
    """
    result = db.query(History).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).update({"is_cleared": True})
    
    db.commit()
    return result


def get_user_history_stats(db: Session, user_id: int) -> HistoryStats:
    """
    Get comprehensive listening statistics for a user
    """
    
    total_listens = db.query(func.count(History.id)).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).scalar()
    
    unique_songs = db.query(func.count(func.distinct(History.song_id))).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).scalar()
    
    total_duration = db.query(func.sum(Song.song_duration)).join(History).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).scalar() or 0
    
    most_listened_song = db.query(Song, func.count(History.id).label('play_count')).join(History).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).group_by(Song.id).order_by(desc('play_count')).first()
    
    most_listened_artist = db.query(
        Artist.artist_stage_name, func.count(History.id).label('play_count')
    ).select_from(History).join(Song).join(Artist).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).group_by(Artist.artist_stage_name).order_by(desc('play_count')).first()
    
    most_listened_genre = db.query(
        Genre.name, func.count(History.id).label('play_count')
    ).select_from(History).join(Song).join(Genre).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).group_by(Genre.name).order_by(desc('play_count')).first()
    
    last_listened = db.query(History.played_at).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).order_by(desc(History.played_at)).first()
    listening_streak = _calculate_listening_streak(db, user_id)
    
    return HistoryStats(
        total_listens=total_listens,
        unique_songs=unique_songs,
        total_duration=total_duration,
        most_listened_song=most_listened_song[0] if most_listened_song else None,
        most_listened_artist=most_listened_artist[0] if most_listened_artist else None,
        most_listened_genre=most_listened_genre[0] if most_listened_genre else None,
        listening_streak=listening_streak,
        last_listened=last_listened[0] if last_listened else None
    )


def get_global_history_stats(db: Session) -> GlobalHistoryStats:
    """
    Get global listening statistics for admin dashboard
    """
    total_listens = db.query(func.count(History.id)).filter(History.is_cleared == False).scalar()
    unique_songs = db.query(func.count(func.distinct(History.song_id))).filter(History.is_cleared == False).scalar()
    unique_users = db.query(func.count(func.distinct(History.user_id))).filter(History.is_cleared == False).scalar()
    
    average_listens_per_user = total_listens / unique_users if unique_users > 0 else 0
    
    most_listened_song = db.query(Song, func.count(History.id).label('play_count')).join(History).filter(
        History.is_cleared == False
    ).group_by(Song.id).order_by(desc('play_count')).first()
    
    most_listened_artist = db.query(
        Artist.artist_stage_name, func.count(History.id).label('play_count')
    ).select_from(History).join(Song).join(Artist).filter(History.is_cleared == False).group_by(Artist.artist_stage_name).order_by(desc('play_count')).first()
    
    most_listened_genre = db.query(
        Genre.name, func.count(History.id).label('play_count')
    ).select_from(History).join(Song).join(Genre).filter(History.is_cleared == False).group_by(Genre.name).order_by(desc('play_count')).first()
    
    return GlobalHistoryStats(
        total_listens=total_listens,
        unique_songs=unique_songs,
        unique_users=unique_users,
        most_listened_song=most_listened_song[0] if most_listened_song else None,
        most_listened_artist=most_listened_artist[0] if most_listened_artist else None,
        most_listened_genre=most_listened_genre[0] if most_listened_genre else None,
        average_listens_per_user=average_listens_per_user
    )


def count_song_plays(db: Session, song_id: int) -> int:
    """
    Get total play count for a specific song (public endpoint)
    """
    return db.query(func.count(History.id)).filter(
        and_(
            History.song_id == song_id,
            History.is_cleared == False
        )
    ).scalar()


def _calculate_listening_streak(db: Session, user_id: int) -> int:
    """
    Calculate consecutive days of listening for a user
    """
    listening_dates = db.query(
        func.date(History.played_at).label('listen_date')
    ).filter(
        and_(
            History.user_id == user_id,
            History.is_cleared == False
        )
    ).distinct().order_by(desc('listen_date')).all()
    
    if not listening_dates:
        return 0
    
    dates = [date[0] for date in listening_dates]
    
    streak = 1
    current_date = dates[0]
    
    for i in range(1, len(dates)):
        if (current_date - dates[i]).days == 1:
            streak += 1
            current_date = dates[i]
        else:
            break
    
    return streak
