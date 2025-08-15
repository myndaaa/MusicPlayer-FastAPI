from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
import secrets
from app.db.models.playlist import Playlist
from app.db.models.playlist_collaborator import PlaylistCollaborator
from app.db.models.user import User
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistStats


def create_playlist(db: Session, playlist_data: PlaylistCreate, owner_id: int) -> Playlist:
    """
    Create a new playlist for a user
    """
    existing_playlist = db.query(Playlist).filter(
        and_(
            Playlist.owner_id == owner_id,
            Playlist.name == playlist_data.name
        )
    ).first()
    
    if existing_playlist:
        raise ValueError(f"Playlist with name '{playlist_data.name}' already exists")
    
    playlist = Playlist(
        owner_id=owner_id,
        name=playlist_data.name,
        description=playlist_data.description
    )
    
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


def get_playlist_by_id(db: Session, playlist_id: int) -> Optional[Playlist]:
    """
    Get a playlist by ID
    """
    return db.query(Playlist).filter(Playlist.id == playlist_id).first()


def get_playlist_with_owner(db: Session, playlist_id: int) -> Optional[Playlist]:
    """
    Get a playlist with owner details
    """
    return db.query(Playlist).options(
        joinedload(Playlist.owner)
    ).filter(Playlist.id == playlist_id).first()


def get_user_playlists(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 20
) -> Tuple[List[Playlist], int]:
    """
    Get playlists owned by a user, paginated
    """
    query = db.query(Playlist).filter(Playlist.owner_id == user_id)
    total = query.count()
    playlists = query.order_by(desc(Playlist.created_at)).offset(skip).limit(limit).all()
    
    return playlists, total


def get_user_playlists_with_owner(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 20
) -> Tuple[List[Playlist], int]:
    """
    Get playlists owned by a user with owner details, paginated
    """
    query = db.query(Playlist).options(
        joinedload(Playlist.owner)
    ).filter(Playlist.owner_id == user_id)
    
    total = query.count()
    playlists = query.order_by(desc(Playlist.created_at)).offset(skip).limit(limit).all()
    
    return playlists, total


def search_playlists(
    db: Session, 
    query: str, 
    user_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 20
) -> Tuple[List[Playlist], int]:
    """
    Search playlists by name or description
    """
    search_filter = Playlist.name.ilike(f"%{query}%") | Playlist.description.ilike(f"%{query}%")
    
    if user_id:
        db_query = db.query(Playlist).filter(
            and_(
                search_filter,
                Playlist.owner_id == user_id
            )
        )
    else:
        db_query = db.query(Playlist).filter(search_filter)
    
    total = db_query.count()
    playlists = db_query.order_by(desc(Playlist.created_at)).offset(skip).limit(limit).all()
    
    return playlists, total


def update_playlist(
    db: Session, 
    playlist_id: int, 
    playlist_data: PlaylistUpdate
) -> Optional[Playlist]:
    """
    Update playlist information
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        return None
    
    if playlist_data.name and playlist_data.name != playlist.name:
        existing_playlist = db.query(Playlist).filter(
            and_(
                Playlist.owner_id == playlist.owner_id,
                Playlist.name == playlist_data.name,
                Playlist.id != playlist_id
            )
        ).first()
        
        if existing_playlist:
            raise ValueError(f"Playlist with name '{playlist_data.name}' already exists")
    
    if playlist_data.name is not None:
        playlist.name = playlist_data.name
    if playlist_data.description is not None:
        playlist.description = playlist_data.description
    
    db.commit()
    db.refresh(playlist)
    return playlist


def delete_playlist(db: Session, playlist_id: int) -> bool:
    """
    Delete a playlist
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        return False
    
    db.delete(playlist)
    db.commit()
    return True


def user_can_edit_playlist(db: Session, user_id: int, playlist_id: int) -> bool:
    """
    Check if user can edit a playlist (owner or collaborator with can_edit=True)
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        return False
    
    if playlist.owner_id == user_id:
        return True

    collaborator = db.query(PlaylistCollaborator).filter(
        and_(
            PlaylistCollaborator.playlist_id == playlist_id,
            PlaylistCollaborator.collaborator_id == user_id,
            PlaylistCollaborator.can_edit == True
        )
    ).first()
    
    return collaborator is not None


def user_can_view_playlist(db: Session, user_id: int, playlist_id: int) -> bool:
    """
    Check if user can view a playlist (owner or collaborator)
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        return False
    
    if playlist.owner_id == user_id:
        return True

    collaborator = db.query(PlaylistCollaborator).filter(
        and_(
            PlaylistCollaborator.playlist_id == playlist_id,
            PlaylistCollaborator.collaborator_id == user_id
        )
    ).first()
    
    return collaborator is not None


def get_playlist_stats(db: Session, playlist_id: int) -> PlaylistStats:
    """
    Get basic statistics for a playlist
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        raise ValueError("Playlist not found")
    
    return PlaylistStats(
        total_playlists=1,
        total_owned_playlists=1,
        total_collaborated_playlists=0,
        created_at=playlist.created_at,
        last_modified=playlist.created_at  
    )


def get_user_playlist_stats(db: Session, user_id: int) -> PlaylistStats:
    """
    Get playlist statistics for a user
    """
    total_owned = db.query(Playlist).filter(Playlist.owner_id == user_id).count()
    
    total_collaborated = db.query(PlaylistCollaborator).filter(
        PlaylistCollaborator.collaborator_id == user_id
    ).count()
    
    return PlaylistStats(
        total_playlists=total_owned + total_collaborated,
        total_owned_playlists=total_owned,
        total_collaborated_playlists=total_collaborated,
        created_at=db.query(func.min(Playlist.created_at)).filter(Playlist.owner_id == user_id).scalar(),
        last_modified=db.query(func.max(Playlist.created_at)).filter(Playlist.owner_id == user_id).scalar()
    )
# helpers
def generate_share_token() -> str:
    """
    Generate a secure share token
    """
    return secrets.token_urlsafe(32)


def generate_collaboration_link(db: Session, playlist_id: int) -> str:
    """
    Generate a collaboration link for a playlist
    """
    playlist = get_playlist_by_id(db, playlist_id)
    if not playlist:
        raise ValueError("Playlist not found")
    
    collaboration_token = generate_share_token()
    
    playlist.share_token = collaboration_token
    playlist.allow_collaboration = True
    db.commit()
    
    return f"http://localhost:8000/playlist/collaborate/{collaboration_token}"


def access_playlist_by_token(db: Session, token: str) -> Optional[Playlist]:
    """
    Access a playlist using a share token
    """
    return db.query(Playlist).filter(Playlist.share_token == token).first()


