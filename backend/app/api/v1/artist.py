from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.artist import Artist
from app.schemas.artist import (
    ArtistCreate, ArtistOut, ArtistSignup, ArtistStats, 
    ArtistWithRelations, ArtistProfileUpdate, ArtistAdminUpdate
)
from app.crud.artist import (
    create_artist_with_user, get_artist_by_id, get_artist_by_user_id,
    get_artist_by_stage_name, get_all_artists, get_all_active_artists,
    search_artists_by_name, update_artist, update_artist_by_user_id,
    disable_artist, enable_artist, delete_artist, artist_exists,
    get_artist_with_related_entities, get_artists_followed_by_user, 
    get_artist_statistics
)
from core.deps import (
    get_current_active_user, get_current_admin, get_current_musician
)

router = APIRouter()


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_artist_signup(
    artist_signup_data: ArtistSignup,
    db: Session = Depends(get_db)
):
    """
    Create a new artist account with user profile.
    
    Creates both user (with musician role) and artist profile in one transaction.
    Validates unique constraints for username, email, and stage name.
    
    Returns: 201 Created - Artist account successfully created
    Returns: 409 Conflict - Username/email/stage name already exists
    """
    try:
        user, artist = create_artist_with_user(db, artist_signup_data)
        return {
            "message": "Artist account created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            },
            "artist": {
                "id": artist.id,
                "stage_name": artist.artist_stage_name,
                "bio": artist.artist_bio
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create artist account"
        )


@router.get("/", response_model=List[ArtistOut])
async def get_artists_public(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, min_length=1, description="Search artists by stage name"),
    active_only: bool = Query(True, description="Return only active artists")
):
    """
    Get list of artists with optional filtering and pagination.
    Public endpoint for browsing artists.
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - search: Search artists by stage name
    - active_only: Return only active artists (default: True)
    
    Returns: 200 OK - List of artists
    """
    if search:
        artists = search_artists_by_name(db, search, skip=skip, limit=limit)
    elif active_only:
        artists = get_all_active_artists(db, skip=skip, limit=limit)
    else:
        artists = get_all_artists(db, skip=skip, limit=limit)
    
    return artists


@router.get("/followed", response_model=List[ArtistOut])
async def get_followed_artists(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get artists that the current user follows.
    Returns paginated list of artists that the authenticated user follows.
    Requires authentication.
    Returns: 200 OK - List of followed artists
    """
    followed_artists = get_artists_followed_by_user(db, current_user.id, skip=skip, limit=limit)
    return followed_artists


@router.get("/{artist_id}", response_model=ArtistOut)
async def get_artist_public(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public artist profile by ID.
    Returns basic artist information for public viewing.
    Only active artists are returned.
    Returns: 200 OK - Artist profile found
    Returns: 404 Not Found - Artist not found or inactive
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist or artist.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    return artist


@router.get("/stage-name/{stage_name}", response_model=ArtistOut)
async def get_artist_by_stage_name_public(
    stage_name: str,
    db: Session = Depends(get_db)
):
    """
    Get public artist profile by stage name.
    Returns basic artist information for public viewing.
    Only active artists are returned.
    Returns: 200 OK - Artist profile found
    Returns: 404 Not Found - Artist not found or inactive
    """
    artist = get_artist_by_stage_name(db, stage_name)
    if not artist or artist.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    
    return artist


@router.get("/me/profile", response_model=ArtistOut)
async def get_current_artist_profile(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Get current artist's profile information.
    Returns the authenticated artist's profile data.
    Requires musician authentication.
    Returns: 200 OK - Current artist profile
    Returns: 404 Not Found - Artist profile not found
    """
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    return artist


@router.put("/me/profile", response_model=ArtistOut)
async def update_current_artist_profile(
    artist_data: ArtistProfileUpdate,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Update current artist's profile information.
    Allows artists to update their own profile data.
    Cannot change linked user account.
    Requires musician authentication.
    Returns: 200 OK - Updated artist profile
    Returns: 400 Bad Request - Invalid data
    Returns: 404 Not Found - Artist profile not found
    """
    updated_artist = update_artist_by_user_id(db, current_user.id, artist_data)
    if not updated_artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    return updated_artist


@router.patch("/me/profile", response_model=ArtistOut)
async def partial_update_current_artist_profile(
    artist_data: ArtistProfileUpdate,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Partially update current artist's profile information.
    Allows artists to update specific fields of their profile.
    Cannot change linked user account.
    Requires musician authentication.
    Returns: 200 OK - Updated artist profile
    Returns: 400 Bad Request - Invalid data
    Returns: 404 Not Found - Artist profile not found
    """
    updated_artist = update_artist_by_user_id(db, current_user.id, artist_data)
    if not updated_artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    return updated_artist


@router.get("/me/with-relations", response_model=ArtistWithRelations)
async def get_current_artist_with_relations(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Get current artist's profile with related entities.
    Returns artist profile with eager-loaded relationships (songs, albums, followers).
    Requires musician authentication.
    Returns: 200 OK - Artist profile with relations
    Returns: 404 Not Found - Artist profile not found
    """
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    artist_with_relations = get_artist_with_related_entities(db, artist.id)
    if not artist_with_relations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    return artist_with_relations


@router.get("/me/followers", response_model=List[dict])
async def get_current_artist_followers(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Get current artist's followers.
    Returns paginated list of users who follow the current artist.
    Requires musician authentication.
    Returns: 200 OK - List of followers
    """
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    # TODO: in following crud, then update here to return followers
    return []


@router.post("/", response_model=ArtistOut, status_code=status.HTTP_201_CREATED)
async def create_artist_admin(
    artist_data: ArtistCreate,
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Create a new artist profile linked to existing user (Admin only).
    Admins can create artist profiles for existing users.
    Validates that user exists and isn't already an artist.
    Returns: 201 Created - Artist successfully created
    Returns: 409 Conflict - User already has artist profile
    Returns: 404 Not Found - User not found
    """
    try:
        artist = create_artist_with_user(db, artist_data, user_id)
        return artist
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create artist profile"
        )


@router.get("/admin/artists", response_model=List[ArtistOut])
async def get_all_artists_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(False, description="Return only active artists")
):
    """
    Get all artists with filtering and pagination (Admin only).
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - active_only: Return only active artists
    Returns: 200 OK - List of artists
    """
    if active_only:
        artists = get_all_active_artists(db, skip=skip, limit=limit)
    else:
        artists = get_all_artists(db, skip=skip, limit=limit)
    
    return artists


@router.get("/admin/artists/{artist_id}", response_model=ArtistOut)
async def get_artist_by_id_admin(
    artist_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get artist by ID with full details (Admin only).
    Returns complete artist data including disabled artists.
    Returns: 200 OK - Artist found
    Returns: 404 Not Found - Artist not found
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return artist


@router.put("/admin/artists/{artist_id}", response_model=ArtistOut)
async def update_artist_admin(
    artist_id: int,
    artist_data: ArtistAdminUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Update any artist (Admin only).
    Admins can update any artist's profile including disabled status.
    Validates unique constraints for stage name.
    Returns: 200 OK - Artist updated successfully
    Returns: 404 Not Found - Artist not found
    Returns: 409 Conflict - Stage name already taken
    """
    try:
        updated_artist = update_artist(db, artist_id, artist_data)
        if not updated_artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        return updated_artist
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.patch("/admin/artists/{artist_id}", response_model=ArtistOut)
async def partial_update_artist_admin(
    artist_id: int,
    artist_data: ArtistAdminUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Partially update any artist (Admin only).
    Same as PUT but semantically indicates partial updates.
    Returns: 200 OK - Artist updated successfully
    Returns: 404 Not Found - Artist not found
    Returns: 409 Conflict - Stage name already taken
    """
    try:
        updated_artist = update_artist(db, artist_id, artist_data)
        if not updated_artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        return updated_artist
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/admin/artists/{artist_id}/disable")
async def disable_artist_admin(
    artist_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Disable an artist account (Admin only).
    Sets is_disabled to True and records disabled_at timesamp.
    Returns: 200 OK - Artist disabled successfully
    Returns: 404 Not Found - Artist not found
    """
    success = disable_artist(db, artist_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return {"message": "Artist disabled successfully"}


@router.post("/admin/artists/{artist_id}/enable")
async def enable_artist_admin(
    artist_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Enable a disabled artist account (Admin only).
    Sets is_disabled to False and clears disabled_at timestamp.
    Returns: 200 OK - Artist enabled successfully
    Returns: 404 Not Found - Artist not found
    """
    success = enable_artist(db, artist_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return {"message": "Artist enabled successfully"}


@router.delete("/admin/artists/{artist_id}")
async def delete_artist_admin(
    artist_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Delete artist (Admin only).
    Only allows deletion if artist has no related data (songs, albums, etc.).
    Returns: 200 OK - Artist deleted successfully
    Returns: 404 Not Found - Artist not found
    Returns: 400 Bad Request - Cannot delete artist with related data
    """
    success = delete_artist(db, artist_id)
    if not success:
        # Check if artist exists
        if not artist_exists(db, artist_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete artist with related data"
            )
    return {"message": "Artist deleted successfully"}


@router.get("/admin/statistics", response_model=ArtistStats)
async def get_artist_statistics_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get artist statistics (Admin only).
    Returns comprehensive artist statistics for admin dashboard.
    Returns: 200 OK - Artist statistics
    """
    stats = get_artist_statistics(db)
    return stats


@router.get("/admin/search", response_model=List[ArtistOut])
async def search_artists_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Search artists by stage name (Admin only).
    Case-insensitive search with pagination.
    Returns: 200 OK - List of matching artists
    """
    artists = search_artists_by_name(db, keyword, skip=skip, limit=limit)
    return artists 
