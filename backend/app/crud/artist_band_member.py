from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from app.db.models.artist_band_member import ArtistBandMember
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.schemas.artist_band_member import ArtistBandMemberCreate


def create_artist_band_member(db: Session, data: ArtistBandMemberCreate) -> ArtistBandMember:
    """Creates a new artist-band membership"""
    db_obj = ArtistBandMember(**data.model_dump())
    db.add(db_obj)
    db.commit()
    return db_obj


def get_artist_band_member_by_id(db: Session, band_member_id: int) -> Optional[ArtistBandMember]:
    """Gets a membership by its ID"""
    return db.query(ArtistBandMember).filter(ArtistBandMember.band_member_id == band_member_id).first()


def get_memberships_by_artist(db: Session, artist_id: int, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]:
    """Gets all memberships for a specific artist with pagination"""
    return db.query(ArtistBandMember).filter(
        ArtistBandMember.artist_id == artist_id
    ).offset(skip).limit(limit).all()


def get_memberships_by_band(db: Session, band_id: int, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]:
    """Gets all memberships for a specific band with pagination"""
    return db.query(ArtistBandMember).filter(
        ArtistBandMember.band_id == band_id
    ).offset(skip).limit(limit).all()


def get_current_members_by_band(db: Session, band_id: int) -> List[ArtistBandMember]:
    """Gets all current members of a band"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).all()


def get_current_bands_for_artist(db: Session, artist_id: int) -> List[ArtistBandMember]:
    """Gets all current bands for an artist"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.is_current_member == True
        )
    ).all()


def get_former_bands_for_artist(db: Session, artist_id: int) -> List[ArtistBandMember]:
    """Gets all former bands for an artist"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.is_current_member == False
        )
    ).all()


def leave_band(db: Session, artist_id: int, band_id: int, left_at: Optional[datetime] = None) -> Optional[ArtistBandMember]:
    """Marks an artist as having left a band"""
    if not left_at:
        left_at = datetime.now(timezone.utc)
    
    membership = db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).first()
    
    if not membership:
        return None
    
    membership.left_at = left_at
    membership.is_current_member = False
    db.commit()
    db.refresh(membership)
    return membership


def rejoin_band(db: Session, artist_id: int, band_id: int, joined_on: Optional[datetime] = None) -> Optional[ArtistBandMember]:
    """Rejoins an artist to a band"""
    if not joined_on:
        joined_on = datetime.now(timezone.utc)
    
    existing = db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.band_id == band_id
        )
    ).first()
    
    if existing:
        existing.left_at = None
        existing.is_current_member = True
        existing.joined_on = joined_on
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_membership = ArtistBandMember(
            artist_id=artist_id,
            band_id=band_id,
            joined_on=joined_on,
            is_current_member=True
        )
        db.add(new_membership)
        db.commit()
        db.refresh(new_membership)
        return new_membership


def invite_artist_to_band(db: Session, artist_id: int, band_id: int, joined_on: Optional[datetime] = None) -> Optional[ArtistBandMember]:
    """Invites an artist to join a band"""
    if not joined_on:
        joined_on = datetime.now(timezone.utc)
    
    existing = db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).first()
    
    if existing:
        return None  
    
    new_membership = ArtistBandMember(
        artist_id=artist_id,
        band_id=band_id,
        joined_on=joined_on,
        is_current_member=True
    )
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    return new_membership


def remove_artist_from_band(db: Session, artist_id: int, band_id: int, left_at: Optional[datetime] = None) -> Optional[ArtistBandMember]:
    """Removes an artist from a band"""
    if not left_at:
        left_at = datetime.now(timezone.utc)
    
    membership = db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).first()
    
    if not membership:
        return None
    
    membership.left_at = left_at
    membership.is_current_member = False
    db.commit()
    db.refresh(membership)
    return membership


def get_all_memberships(db: Session, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]:
    """Gets all memberships with pagination"""
    return db.query(ArtistBandMember).offset(skip).limit(limit).all()


def search_memberships(db: Session, search_term: str, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]:
    """Searches memberships by artist name or band name"""
    return db.query(ArtistBandMember).join(Artist).join(Band).filter(
        or_(
            Artist.artist_stage_name.ilike(f"%{search_term}%"),
            Band.name.ilike(f"%{search_term}%")
        )
    ).offset(skip).limit(limit).all()


def get_membership_statistics(db: Session) -> dict:
    """Gets membership statistics"""
    total = db.query(ArtistBandMember).count()
    current = db.query(ArtistBandMember).filter(ArtistBandMember.is_current_member == True).count()
    former = total - current
    
    avg_duration = db.query(
        func.avg(
            func.extract('epoch', ArtistBandMember.left_at - ArtistBandMember.joined_on) / 86400
        )
    ).filter(
        and_(
            ArtistBandMember.left_at.isnot(None),
            ArtistBandMember.is_current_member == False
        )
    ).scalar() or 0
    
    return {
        "total_memberships": total,
        "current_memberships": current,
        "former_memberships": former,
        "average_membership_duration": float(avg_duration)
    }


def membership_exists(db: Session, band_member_id: int) -> bool:
    """Checks if a membership exists"""
    return db.query(ArtistBandMember).filter(ArtistBandMember.band_member_id == band_member_id).first() is not None


def is_current_member(db: Session, artist_id: int, band_id: int) -> bool:
    """Checks if an artist is currently a member of a band"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).first() is not None


def get_membership_count_by_band(db: Session, band_id: int) -> int:
    """Gets the number of current members in a band"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.band_id == band_id,
            ArtistBandMember.is_current_member == True
        )
    ).count()


def get_band_count_for_artist(db: Session, artist_id: int) -> int:
    """Gets the number of current bands for an artist"""
    return db.query(ArtistBandMember).filter(
        and_(
            ArtistBandMember.artist_id == artist_id,
            ArtistBandMember.is_current_member == True
        )
    ).count()
