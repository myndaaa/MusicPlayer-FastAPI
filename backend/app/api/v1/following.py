from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user, get_current_admin
from app.db.models.user import User
from app.crud.following import (
    toggle_following,
    is_user_following_artist,
    is_user_following_band,
    get_user_followings,
    get_user_followings_with_targets,
    count_artist_followers,
    count_band_followers,
    get_following_statistics,
    get_user_following_summary
)
from app.schemas.following import (
    FollowingToggle,
    FollowingOut,
    FollowingList,
    FollowingStats,
    UserFollowingSummary,
    FollowingWithTarget
)

router = APIRouter()


# Public endpoints (no auth required)
@router.get("/artist/{artist_id}/count", response_model=dict)
def get_artist_follower_count(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the total number of followers for an artist (public).
    """
    count = count_artist_followers(db, artist_id)
    return {"artist_id": artist_id, "follower_count": count}


@router.get("/band/{band_id}/count", response_model=dict)
def get_band_follower_count(
    band_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the total number of followers for a band (public).
    """
    count = count_band_followers(db, band_id)
    return {"band_id": band_id, "follower_count": count}


# Authenticated user endpoints
@router.post("/toggle", response_model=dict)
def toggle_following_endpoint(
    following_data: FollowingToggle,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle follow/unfollow status for an artist or band.
    """
    following, was_created = toggle_following(
        db, 
        current_user.id, 
        following_data.artist_id, 
        following_data.band_id
    )
    
    action = "followed" if was_created else "unfollowed"
    target_type = "artist" if following_data.artist_id else "band"
    target_id = following_data.artist_id or following_data.band_id
    
    return {
        "message": f"Successfully {action} {target_type}",
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "following_id": following.id if was_created else None
    }


@router.get("/artist/{artist_id}/is-following", response_model=dict)
def check_artist_following_status(
    artist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user is following a specific artist.
    """
    is_following = is_user_following_artist(db, current_user.id, artist_id)
    return {
        "artist_id": artist_id,
        "is_following": is_following,
        "user_id": current_user.id
    }


@router.get("/band/{band_id}/is-following", response_model=dict)
def check_band_following_status(
    band_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user is following a specific band.
    """
    is_following = is_user_following_band(db, current_user.id, band_id)
    return {
        "band_id": band_id,
        "is_following": is_following,
        "user_id": current_user.id
    }


@router.get("/user/me", response_model=FollowingList)
def get_current_user_followings(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all followings by the current user with pagination.
    """
    skip = (page - 1) * per_page
    followings_with_targets = get_user_followings_with_targets(db, current_user.id, skip, per_page)
    
    # Convert to FollowingWithTarget objects
    followings = []
    for following, artist, band in followings_with_targets:
        following_data = {
            "id": following.id,
            "user_id": following.user_id,
            "started_at": following.started_at,
            "artist": artist,
            "band": band
        }
        followings.append(FollowingWithTarget(**following_data))
    
    total = len(followings_with_targets)  # This is a simplified count
    total_pages = (total + per_page - 1) // per_page
    
    return FollowingList(
        followings=followings,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/user/me/artists", response_model=List[dict])
def get_current_user_followed_artists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all artists that the current user is following.
    """
    followings_with_targets = get_user_followings_with_targets(db, current_user.id, skip=0, limit=1000)
    
    followed_artists = []
    for following, artist, band in followings_with_targets:
        if artist:
            followed_artists.append({
                "id": artist.id,
                "artist_stage_name": artist.artist_stage_name,
                "artist_profile_image": artist.artist_profile_image,
                "followed_since": following.started_at
            })
    
    return followed_artists


@router.get("/user/me/bands", response_model=List[dict])
def get_current_user_followed_bands(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all bands that the current user is following.
    """
    followings_with_targets = get_user_followings_with_targets(db, current_user.id, skip=0, limit=1000)
    
    followed_bands = []
    for following, artist, band in followings_with_targets:
        if band:
            followed_bands.append({
                "id": band.id,
                "name": band.name,
                "profile_picture": band.profile_picture,
                "followed_since": following.started_at
            })
    
    return followed_bands


@router.get("/user/me/summary", response_model=UserFollowingSummary)
def get_current_user_following_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of the current user's followings.
    """
    summary = get_user_following_summary(db, current_user.id)
    return UserFollowingSummary(**summary)


# Admin-only endpoints
@router.get("/admin/statistics", response_model=FollowingStats)
def get_following_statistics_admin(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall following statistics (admin only).
    """
    stats = get_following_statistics(db)
    return FollowingStats(**stats)
