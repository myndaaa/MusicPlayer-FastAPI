from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_musician, get_current_admin
from app.crud.artist_band_member import (
    create_artist_band_member,
    get_artist_band_member_by_id,
    get_memberships_by_artist,
    get_memberships_by_band,
    get_current_members_by_band,
    get_current_bands_for_artist,
    get_former_bands_for_artist,
    leave_band,
    rejoin_band,
    invite_artist_to_band,
    remove_artist_from_band,
    get_all_memberships,
    search_memberships,
    get_membership_statistics,
    is_current_member
)
from app.crud.artist import get_artist_by_user_id
from app.crud.band import get_band_by_id, is_band_owner
from app.schemas.artist_band_member import (
    ArtistBandMemberOut,
    ArtistBandMemberCreate,
    ArtistBandMemberJoin,
    ArtistBandMemberLeave,
    ArtistBandMemberRejoin,
    ArtistBandMemberInvite,
    ArtistBandMemberRemove,
    ArtistBandMemberStats
)
from app.db.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ArtistBandMemberOut])
def get_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all memberships with pagination"""
    memberships = get_all_memberships(db, skip=skip, limit=limit)
    return memberships


@router.get("/{band_member_id}", response_model=ArtistBandMemberOut)
def get_membership(band_member_id: int, db: Session = Depends(get_db)):
    """Get a specific membership by ID"""
    membership = get_artist_band_member_by_id(db, band_member_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


@router.get("/artist/{artist_id}", response_model=List[ArtistBandMemberOut])
def get_artist_memberships(
    artist_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all memberships for a specific artist"""
    memberships = get_memberships_by_artist(db, artist_id, skip=skip, limit=limit)
    return memberships


@router.get("/band/{band_id}", response_model=List[ArtistBandMemberOut])
def get_band_memberships(
    band_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all memberships for a specific band"""
    memberships = get_memberships_by_band(db, band_id, skip=skip, limit=limit)
    return memberships


@router.get("/band/{band_id}/current", response_model=List[ArtistBandMemberOut])
def get_current_band_members(band_id: int, db: Session = Depends(get_db)):
    """Get current members of a band"""
    members = get_current_members_by_band(db, band_id)
    return members


@router.get("/artist/{artist_id}/current", response_model=List[ArtistBandMemberOut])
def get_current_artist_bands(artist_id: int, db: Session = Depends(get_db)):
    """Get current bands for an artist"""
    bands = get_current_bands_for_artist(db, artist_id)
    return bands


@router.post("/join", response_model=ArtistBandMemberOut)
def join_band(
    data: ArtistBandMemberJoin,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Join a band (musician can join themselves)"""
    # Get current user's artist profile
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    # Check if already a member
    if is_current_member(db, artist.id, data.band_id):
        raise HTTPException(status_code=409, detail="Already a member of this band")
    
    # Check if band exists
    band = get_band_by_id(db, data.band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    
    joined_on = data.joined_on or datetime.now(timezone.utc)
    membership_data = ArtistBandMemberCreate(
        artist_id=artist.id,
        band_id=data.band_id,
        joined_on=joined_on,
        is_current_member=True
    )
    membership = create_artist_band_member(db, membership_data)
    return membership


@router.post("/leave", response_model=ArtistBandMemberOut)
def leave_band_endpoint(
    data: ArtistBandMemberLeave,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Leave a band (musician can leave themselves)"""
    # Get current user's artist profile
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    # Check if currently a member
    if not is_current_member(db, artist.id, data.band_id):
        raise HTTPException(status_code=404, detail="Not a current member of this band")
    
    left_at = data.left_at or datetime.now(timezone.utc)
    membership = leave_band(db, artist.id, data.band_id, left_at)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


@router.post("/rejoin", response_model=ArtistBandMemberOut)
def rejoin_band_endpoint(
    data: ArtistBandMemberRejoin,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Rejoin a band (musician can rejoin themselves)"""
    # Get current user's artist profile
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    # Check if band exists
    band = get_band_by_id(db, data.band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    
    joined_on = data.joined_on or datetime.now(timezone.utc)
    membership = rejoin_band(db, artist.id, data.band_id, joined_on)
    return membership


@router.get("/me/memberships", response_model=List[ArtistBandMemberOut])
def get_my_memberships(
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Get current user's memberships"""
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    memberships = get_memberships_by_artist(db, artist.id)
    return memberships


@router.get("/me/current-bands", response_model=List[ArtistBandMemberOut])
def get_my_current_bands(
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Get current user's current bands"""
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    bands = get_current_bands_for_artist(db, artist.id)
    return bands


@router.get("/me/former-bands", response_model=List[ArtistBandMemberOut])
def get_my_former_bands(
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Get current user's former bands"""
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist profile not found")
    
    bands = get_former_bands_for_artist(db, artist.id)
    return bands


@router.post("/band/{band_id}/invite", response_model=ArtistBandMemberOut)
def invite_artist_to_band_endpoint(
    band_id: int,
    data: ArtistBandMemberInvite,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Invite an artist to join a band (band owner only)"""
    
    # Check if band exists
    band = get_band_by_id(db, band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    
    # Check if current user is the band owner
    if not is_band_owner(db, band_id, current_user.id):
        raise HTTPException(status_code=403, detail="Only band owner can invite artists")
    
    # Check if artist exists
    artist = get_artist_by_user_id(db, data.artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    # Check if already a member
    if is_current_member(db, artist.id, band_id):
        raise HTTPException(status_code=409, detail="Artist is already a member of this band")
    
    joined_on = data.joined_on or datetime.now(timezone.utc)
    membership = invite_artist_to_band(db, artist.id, band_id, joined_on)
    if not membership:
        raise HTTPException(status_code=409, detail="Failed to invite artist to band")
    return membership


@router.post("/band/{band_id}/remove", response_model=ArtistBandMemberOut)
def remove_artist_from_band_endpoint(
    band_id: int,
    data: ArtistBandMemberRemove,
    current_user: User = Depends(get_current_musician),
    db: Session = Depends(get_db)
):
    """Remove an artist from a band (band owner only)"""
    
    # Check if band exists
    band = get_band_by_id(db, band_id)
    if not band:
        raise HTTPException(status_code=404, detail="Band not found")
    
    # Check if current user is the band owner
    if not is_band_owner(db, band_id, current_user.id):
        raise HTTPException(status_code=403, detail="Only band owner can remove artists")
    
    # Check if artist is currently a member
    if not is_current_member(db, data.artist_id, band_id):
        raise HTTPException(status_code=404, detail="Artist is not a current member of this band")
    
    left_at = data.left_at or datetime.now(timezone.utc)
    membership = remove_artist_from_band(db, data.artist_id, band_id, left_at)
    if not membership:
        raise HTTPException(status_code=404, detail="Failed to remove artist from band")
    return membership


@router.get("/admin/memberships", response_model=List[ArtistBandMemberOut])
def admin_get_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all memberships (admin only)"""
    memberships = get_all_memberships(db, skip=skip, limit=limit)
    return memberships


@router.get("/admin/statistics", response_model=ArtistBandMemberStats)
def admin_get_statistics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get membership statistics (admin only)"""
    stats = get_membership_statistics(db)
    return ArtistBandMemberStats(**stats)


@router.get("/admin/search", response_model=List[ArtistBandMemberOut])
def admin_search_memberships(
    search: str = Query(..., description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Search memberships (admin only)"""
    memberships = search_memberships(db, search, skip=skip, limit=limit)
    return memberships 
