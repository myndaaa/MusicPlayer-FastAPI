from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.artist import Artist
from app.schemas.artist import (
    ArtistCreate, ArtistOut, ArtistSignup, ArtistSignupArtistInfo, ArtistSignupUserInfo, 
    ArtistProfileUpdate, ArtistAdminUpdate, ArtistSignupResponse
)
from app.schemas.user import UserOut
from app.crud.artist import (
    create_artist_with_user, get_artist_by_id, get_artist_by_user_id,
    get_artist_by_stage_name, get_all_artists, get_all_active_artists,
    search_artists_by_name, update_artist, update_artist_by_user_id,
    disable_artist, enable_artist, delete_artist, artist_exists,
    get_artist_with_related_entities, get_artists_followed_by_user
)
from app.core.deps import (
    get_current_active_user, get_current_admin, get_current_musician
)
from app.services.token_service import TokenService
from app.services.email_service import EmailService
from app.dependencies import get_email_service

router = APIRouter()


@router.post("/signup", response_model=ArtistSignupResponse, status_code=status.HTTP_201_CREATED)
async def create_artist_signup(
    artist_signup_data: ArtistSignup,
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
) -> ArtistSignupResponse:
    """
    Creates both user (with musician role) and artist profile in one transaction.
    Validates unique constraints for username, email, and stage name.
    Returns: 201 Created - Artist account successfully created
    Returns: 409 Conflict - Username/email/stage name already exists
    """
    try:
        user, artist = create_artist_with_user(db, artist_signup_data)
        
        token = TokenService.create_token(db, user.id, "email_verification")
        try:
            email_service.send_verification_email(user, token.token)
        except Exception:
            pass
        return ArtistSignupResponse(
            message="Artist account created successfully",
            user=ArtistSignupUserInfo(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            ),
            artist=ArtistSignupArtistInfo(
                id=artist.id,
                stage_name=artist.artist_stage_name,
                bio=artist.artist_bio
            )
        )
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
    active_only: bool = Query(True, description="Return only active artists"),
    artist_id: Optional[int] = Query(None, description="Get specific artist by ID"),
    stage_name: Optional[str] = Query(None, min_length=1, description="Get specific artist by stage name")
):
    """
    Get artists with flexible filtering options.
    Public endpoint for browsing artists.
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - search: Search artists by stage name (returns multiple results)
    - active_only: Return only active artists (default: True)
    - artist_id: Get specific artist by ID (returns single result)
    - stage_name: Get specific artist by stage name (returns single result)

    Returns: 200 OK - List of artists or single artist
    Returns: 404 Not Found - Artist not found (when using artist_id or stage_name)
    """
    
    if artist_id is not None:
        artist = get_artist_by_id(db, artist_id)
        if not artist or artist.is_disabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        return [artist]  
    
    if stage_name is not None:
        artist = get_artist_by_stage_name(db, stage_name)
        if not artist or artist.is_disabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist not found"
            )
        return [artist]  
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


@router.post("/me/disable")
async def disable_current_artist_profile(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Disable current artist's profile.
    Artists can disable their own profiles temporarily.
    Requires musician authentication.
    Returns: 200 OK - Artist profile disabled successfully
    Returns: 404 Not Found - Artist profile not found
    """
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    success = disable_artist(db, artist.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to disable artist profile"
        )
    return {"message": "Artist profile disabled successfully"}


@router.get("/me/profile", response_model=ArtistOut)
async def get_current_artist_profile(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db),
    include_songs: bool = Query(False, description="Include artist's songs"),
    include_albums: bool = Query(False, description="Include artist's albums"),
    include_followers: bool = Query(False, description="Include artist's followers")
):
    """
    Get current artist's profile with optional related data.
    Use query parameters to include specific related entities.
    Requires musician authentication.
    Returns: 200 OK - Artist profile with requested relations
    Returns: 404 Not Found - Artist profile not found
    """
    artist = get_artist_by_user_id(db, current_user.id)
    if not artist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist profile not found"
        )
    
    if include_songs or include_albums or include_followers:
        artist = get_artist_with_related_entities(db, artist.id)
        if not artist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artist profile not found"
            )
    
    return artist


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

    # TODO: in following update to return followers
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
    Admins can re-enable artist profiles that were disabled by the artists themselves.
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
 
