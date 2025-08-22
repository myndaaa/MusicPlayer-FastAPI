from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
from app.db.models.playlist_collaborator import PlaylistCollaborator
from app.db.models.playlist import Playlist
from app.db.models.user import User
from app.schemas.playlist_collaborator import PlaylistCollaboratorCreate, PlaylistCollaboratorUpdate, PlaylistCollaboratorStats


def add_collaborator_to_playlist(
    db: Session, 
    playlist_id: int, 
    collaborator_id: int, 
    added_by_user_id: int,
    can_edit: bool = False
) -> PlaylistCollaborator:
    """
    Add a collaborator to a playlist
    """
    existing_collaborator = get_collaborator_entry(db, playlist_id, collaborator_id)
    if existing_collaborator:
        raise ValueError("User is already a collaborator on this playlist")
    
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist or playlist.owner_id != added_by_user_id:
        raise ValueError("Only playlist owner can add collaborators")
    
    if collaborator_id == playlist.owner_id:
        raise ValueError("Cannot add playlist owner as collaborator")
    
    playlist_collaborator = PlaylistCollaborator(
        playlist_id=playlist_id,
        collaborator_id=collaborator_id,
        can_edit=can_edit,
        added_by_user_id=added_by_user_id
    )
    
    db.add(playlist_collaborator)
    db.commit()
    db.refresh(playlist_collaborator)
    return playlist_collaborator


def get_collaborator_entry(
    db: Session, 
    playlist_id: int, 
    user_id: int
) -> Optional[PlaylistCollaborator]:
    """
    Get a specific collaborator entry
    """
    return db.query(PlaylistCollaborator).filter(
        and_(
            PlaylistCollaborator.playlist_id == playlist_id,
            PlaylistCollaborator.collaborator_id == user_id
        )
    ).first()


def get_playlist_collaborators(
    db: Session, 
    playlist_id: int,
    skip: int = 0,
    limit: int = 50
) -> Tuple[List[PlaylistCollaborator], int]:
    """
    Get all collaborators for a playlist
    """
    query = db.query(PlaylistCollaborator).options(
        joinedload(PlaylistCollaborator.collaborator),
        joinedload(PlaylistCollaborator.added_by)
    ).filter(PlaylistCollaborator.playlist_id == playlist_id)
    
    total = query.count()
    collaborators = query.order_by(desc(PlaylistCollaborator.added_at)).offset(skip).limit(limit).all()
    
    return collaborators, total


def remove_collaborator_from_playlist(
    db: Session, 
    playlist_id: int, 
    collaborator_id: int
) -> bool:
    """
    Remove a collaborator from a playlist
    """
    playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if not playlist:
        return False
    
    collaborator = get_collaborator_entry(db, playlist_id, collaborator_id)
    if not collaborator:
        return False
    
    db.delete(collaborator)
    db.commit()
    return True


def get_playlist_collaborator_stats(db: Session, playlist_id: int) -> PlaylistCollaboratorStats:
    """
    Get statistics for playlist collaborators
    """
    
    collaborator_stats = db.query(
        func.count(PlaylistCollaborator.id).label('total_collaborators'),
        func.sum(PlaylistCollaborator.can_edit.cast(func.Integer)).label('can_edit_count')
    ).filter(PlaylistCollaborator.playlist_id == playlist_id).first()
    
    most_collaborative = db.query(
        User, func.count(PlaylistCollaborator.id).label('collab_count')
    ).join(PlaylistCollaborator).group_by(User.id).order_by(desc('collab_count')).first()
    
    return PlaylistCollaboratorStats(
        total_collaborators=collaborator_stats.total_collaborators or 0,
        can_edit_collaborators=collaborator_stats.can_edit_count or 0,
        read_only_collaborators=(collaborator_stats.total_collaborators or 0) - (collaborator_stats.can_edit_count or 0),
        most_collaborative_user=most_collaborative[0] if most_collaborative else None
    )
