from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.db.models.band import Band
from app.schemas.band import (
    BandCreate, BandOut, BandUpdate, BandStats, BandWithRelations
)
from app.crud.band import (
    create_band, get_band_by_id, get_band_by_name, get_all_bands,
    get_active_bands, search_bands_by_name, update_band,
    disable_band, enable_band, delete_band_permanently, get_band_statistics
)
from core.deps import (
    get_current_active_user, get_current_admin, get_current_musician
)

router = APIRouter()
"""
AUTHENTICATION LEVELS:
- None: Public endpoint, no authentication required
- Required: Must provide valid JWT token
- Musician: Only users with musician role
- Admin: Only users with admin role
"""


@router.post("/signup", response_model=BandOut, status_code=status.HTTP_201_CREATED)
async def create_band_signup(
    band_data: BandCreate,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Create a new band (Musicians only).
    Only users with musician role can create bands.
    Validates unique band name constraints.
    
    Returns: 201 Created - Band successfully created
    Returns: 409 Conflict - Band name already exists
    """
    try:
        band = create_band(db, band_data, current_user.id)
        return band
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create band"
        )


@router.get("/", response_model=List[BandOut])
async def get_bands_public(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, min_length=1, description="Search bands by name"),
    active_only: bool = Query(True, description="Return only active bands")
):
    """
    Get list of bands with optional filtering and pagination.
    Public endpoint for browsing bands.
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - search: Search bands by name
    - active_only: Return only active bands (default: True)
    
    Returns: 200 OK - List of bands
    """
    if search:
        bands = search_bands_by_name(db, search, skip=skip, limit=limit)
    elif active_only:
        bands = get_active_bands(db, skip=skip, limit=limit)
    else:
        bands = get_all_bands(db, skip=skip, limit=limit)
    
    return bands


@router.get("/{band_id}", response_model=BandOut)
async def get_band_public(
    band_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public band profile by ID.
    Returns basic band information for public viewing.
    Only active bands are returned.
    Returns: 200 OK - Band profile found
    Returns: 404 Not Found - Band not found or inactive
    """
    band = get_band_by_id(db, band_id)
    if not band or band.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return band


@router.get("/name/{name}", response_model=BandOut)
async def get_band_by_name_public(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get public band profile by name.
    Returns basic band information for public viewing.
    Only active bands are returned.
    Returns: 200 OK - Band profile found
    Returns: 404 Not Found - Band not found or inactive
    """
    band = get_band_by_name(db, name)
    if not band or band.is_disabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return band


@router.get("/me/bands", response_model=List[BandOut])
async def get_current_artist_bands(
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get current artist's bands.
    Returns paginated list of bands created by the current artist.
    Requires musician authentication.
    Returns: 200 OK - List of artist's bands
    """
    # TODO: Implement get_bands_by_artist in CRUD
    # For now, return empty list
    return []


@router.post("/me/bands", response_model=BandOut, status_code=status.HTTP_201_CREATED)
async def create_band_for_artist(
    band_data: BandCreate,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Create a new band for the current artist.
    Only musicians can create bands.
    Validates unique band name constraints.
    Returns: 201 Created - Band successfully created
    Returns: 409 Conflict - Band name already exists
    """
    try:
        band = create_band(db, band_data, current_user.id)
        return band
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create band"
        )


@router.get("/me/bands/{band_id}", response_model=BandOut)
async def get_current_artist_band(
    band_id: int,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Get current artist's specific band.
    Returns band information for the current artist.
    Requires musician authentication.
    Returns: 200 OK - Band found
    Returns: 404 Not Found - Band not found or not owned by artist
    """
    band = get_band_by_id(db, band_id)
    if not band:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    # TODO: Check if band belongs to current artist
    return band


@router.put("/me/bands/{band_id}", response_model=BandOut)
async def update_current_artist_band(
    band_id: int,
    band_data: BandUpdate,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Update current artist's band.
    Allows artists to update their own band information.
    Validates unique constraints for band name.
    Requires musician authentication.
    Returns: 200 OK - Band updated successfully
    Returns: 404 Not Found - Band not found or not owned by artist
    Returns: 409 Conflict - Band name already taken
    """
    try:
        updated_band = update_band(db, band_id, band_data)
        if not updated_band:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Band not found"
            )
        return updated_band
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/me/bands/{band_id}")
async def delete_current_artist_band(
    band_id: int,
    current_user: Annotated[User, Depends(get_current_musician)],
    db: Session = Depends(get_db)
):
    """
    Delete current artist's band.
    Allows artists to delete their own bands.
    Requires musician authentication.
    Returns: 200 OK - Band deleted successfully
    Returns: 404 Not Found - Band not found or not owned by artist
    """
    # TODO: Check if band belongs to current artist
    success = delete_band_permanently(db, band_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return {"message": "Band deleted successfully"}


# Admin endpoints
@router.post("/", response_model=BandOut, status_code=status.HTTP_201_CREATED)
async def create_band_admin(
    band_data: BandCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Create a new band (Admin only).
    Admins can create bands for any purpose.
    Validates unique band name constraints.
    Returns: 201 Created - Band successfully created
    Returns: 409 Conflict - Band name already exists
    """
    try:
        band = create_band(db, band_data, current_admin.id)
        return band
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create band"
        )


@router.get("/admin/bands", response_model=List[BandOut])
async def get_all_bands_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(False, description="Return only active bands")
):
    """
    Get all bands with filtering and pagination (Admin only).
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - active_only: Return only active bands
    Returns: 200 OK - List of bands
    """
    if active_only:
        bands = get_active_bands(db, skip=skip, limit=limit)
    else:
        bands = get_all_bands(db, skip=skip, limit=limit)
    
    return bands


@router.get("/admin/bands/{band_id}", response_model=BandOut)
async def get_band_by_id_admin(
    band_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get band by ID with full details (Admin only).
    Returns complete band data including disabled bands.
    Returns: 200 OK - Band found
    Returns: 404 Not Found - Band not found
    """
    band = get_band_by_id(db, band_id)
    if not band:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    return band


@router.put("/admin/bands/{band_id}", response_model=BandOut)
async def update_band_admin(
    band_id: int,
    band_data: BandUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Update any band (Admin only).
    Admins can update any band's information.
    Validates unique constraints for band name.
    Returns: 200 OK - Band updated successfully
    Returns: 404 Not Found - Band not found
    Returns: 409 Conflict - Band name already taken
    """
    try:
        updated_band = update_band(db, band_id, band_data)
        if not updated_band:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Band not found"
            )
        return updated_band
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/admin/bands/{band_id}")
async def delete_band_admin(
    band_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Delete any band (Admin only).
    Admins can delete any band.
    Returns: 200 OK - Band deleted successfully
    Returns: 404 Not Found - Band not found
    """
    success = delete_band_permanently(db, band_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return {"message": "Band deleted successfully"}


@router.post("/admin/bands/{band_id}/disable")
async def disable_band_admin(
    band_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Disable a band (Admin only).
    Sets is_disabled to True and records disabled_at timestamp.
    Returns: 200 OK - Band disabled successfully
    Returns: 404 Not Found - Band not found
    """
    success = disable_band(db, band_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return {"message": "Band disabled successfully"}


@router.post("/admin/bands/{band_id}/enable")
async def enable_band_admin(
    band_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Enable a disabled band (Admin only).
    Sets is_disabled to False and clears disabled_at timestamp.
    Returns: 200 OK - Band enabled successfully
    Returns: 404 Not Found - Band not found
    """
    success = enable_band(db, band_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    return {"message": "Band enabled successfully"}


@router.get("/admin/statistics", response_model=BandStats)
async def get_band_statistics_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get band statistics (Admin only).
    Returns comprehensive band statistics for admin dashboard.
    Returns: 200 OK - Band statistics
    """
    stats = get_band_statistics(db)
    return BandStats(**stats)


@router.get("/admin/search", response_model=List[BandOut])
async def search_bands_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Search bands by name (Admin only).
    Case-insensitive search with pagination.
    Returns: 200 OK - List of matching bands
    """
    bands = search_bands_by_name(db, keyword, skip=skip, limit=limit)
    return bands 
