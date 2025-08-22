from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserPasswordUpdate, UserOut, UserRole,
    UserLogin, UserInDB, UserSignup
)
from app.crud.user import (
    create_user, get_user_by_id, get_user_by_username, get_user_by_email,
    update_user, change_password, activate_user, deactivate_user,
    get_users_paginated, search_users_by_name, get_users_by_role,
    get_active_users,
    get_user_playlists, get_user_likes, get_user_history,
    get_user_subscriptions, get_user_payments, get_user_audit_logs,
    bulk_update_user_status, get_user_count_by_role, get_active_user_count,
    
)
from app.api.v1.deps import (
    get_current_active_user, get_current_admin
)

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_signup(
    user_data: UserSignup, 
    db: Session = Depends(get_db)
):
    """
    Create a new user account
    - Validates user data and password strength
    - Checks for unique username and email
    - Automatically sets role to 'listener'
    - Creates active user account
    
    Returns: 201 Created - User successfully created
    """
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # 409 Conflict resource already exists
            detail="Username already registered"
        )
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # 409 Conflict resource already exists
            detail="Email already registered"
        )
    
    try:
        # Create UserCreate object with role set to listener
        user_create_data = UserCreate(
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=user_data.password,
            role=UserRole.listener  # Default role for signup
        )
        
        user = create_user(db, user_create_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request invalid data
            detail="Failed to create user account"
        )


@router.get("/", response_model=List[UserOut])
async def get_users_public(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, min_length=1, description="Search users by name"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    active_only: bool = Query(True, description="Return only active users")
):
    """
    Get list of users with optional filtering and pagination.
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - search: Search users by first or last name
    - role: Filter by user role
    - active_only: Return only active users (default: True)
    Returns: 200 OK - List of users
    """
    if search:
        users = search_users_by_name(db, search)
    elif role:
        users = get_users_by_role(db, role, skip=skip, limit=limit)
    elif active_only:
        users = get_active_users(db, skip=skip, limit=limit)
    else:
        users = get_users_paginated(db, skip=skip, limit=limit)
    
    return users


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user's profile information.
    
    Returns the authenticated user's profile data.
    Requires authentication.
    
    Returns: 200 OK - Current user profile
    """
    return current_user


@router.put("/me", response_model=UserOut)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    
    Allows users to update their own profile data.
    Cannot change role or sensitive fields.
    Requires authentication.
    
    Returns: 200 OK - Updated user profile
    Returns: 400 Bad Request - Invalid data
    """
    updated_user = update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request - invalid data
            detail="Failed to update user profile"
        )
    return updated_user


@router.patch("/me", response_model=UserOut)
async def partial_update_current_user_profile(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Partially update current user's profile information.
    
    Allows users to update specific fields of their profile.
    Cannot change role or sensitive fields.
    Requires authentication.
    
    Returns: 200 OK - Updated user profile
    Returns: 400 Bad Request - Invalid data
    """
    updated_user = update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request - invalid data
            detail="Failed to update user profile"
        )
    return updated_user


@router.put("/me/password")
async def update_current_user_password(
    password_data: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user's password.
    
    Requires current password verification.
    Validates new password strength.
    Requires authentication.
    
    Returns: 200 OK - Password updated successfully
    Returns: 400 Bad Request - Invalid password data
    Returns: 401 Unauthorized - Current password incorrect
    """
    success = change_password(db, current_user.id, password_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request - invalid password
            detail="Failed to update password"
        )
    return {"message": "Password updated successfully"}


@router.delete("/me")
async def delete_current_user_account(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Delete current user's account.
    
    Permanently deactivates the user account.
    Requires authentication.
    
    Returns: 200 OK - Account deleted successfully
    """
    # Deactivate user instead of hard delete for data integrity
    success = deactivate_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 Bad Request - failed to delete
            detail="Failed to delete user account"
        )
    return {"message": "Account deleted successfully"}


@router.get("/me/playlists")
async def get_current_user_playlists(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return")
):
    """
    Get current user's playlists.
    
    Returns paginated list of user's playlists.
    Requires authentication.
    
    Returns: 200 OK - List of playlists
    """
    playlists = get_user_playlists(db, current_user.id, skip=skip, limit=limit)
    return playlists


@router.get("/me/likes")
async def get_current_user_likes(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Get current user's liked songs.
    
    Returns paginated list of user's liked songs.
    Requires authentication.
    
    Returns: 200 OK - List of liked songs
    """
    likes = get_user_likes(db, current_user.id, skip=skip, limit=limit)
    return likes


@router.get("/me/history")
async def get_current_user_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return")
):
    """
    Get current user's listening history.
    
    Returns paginated list of user's listening history.
    Requires authentication.
    
    Returns: 200 OK - List of history records
    """
    history = get_user_history(db, current_user.id, skip=skip, limit=limit)
    return history


@router.get("/me/subscriptions")
async def get_current_user_subscriptions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Get current user's subscription information.
    
    Returns paginated list of user's subscriptions.
    Requires authentication.
    
    Returns: 200 OK - List of subscriptions
    """
    subscriptions = get_user_subscriptions(db, current_user.id, skip=skip, limit=limit)
    return subscriptions


@router.get("/me/payments")
async def get_current_user_payments(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return")
):
    """
    Get current user's payment history.
    
    Returns paginated list of user's payment records.
    Requires authentication.
    
    Returns: 200 OK - List of payment records
    """
    payments = get_user_payments(db, current_user.id, skip=skip, limit=limit)
    return payments


@router.get("/{user_id}", response_model=UserOut)
async def get_user_public_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public user profile by ID.
    
    Returns basic user information for public viewing.
    Only active users are returned.
    
    Returns: 200 OK - User profile found
    Returns: 404 Not Found - User not found or inactive
    """
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # 404 Not Found - resource doesn't exist
            detail="User not found"
        )
    
    return user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: UserCreate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only).
    - Admins can create users with any role
    - Validates unique constraints
    - Creates active user account
    
    Returns: 201 Created - User successfully created
    Returns: 409 Conflict - Username/email already exists
    """
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        user = create_user(db, user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user account"
        )


@router.get("/admin/users", response_model=List[UserOut])
async def get_all_users_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    active_only: bool = Query(False, description="Return only active users")
):
    """
    Get all users with filtering and pagination (Admin only).
    Query Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (pagination)
    - role: Filter by user role
    - active_only: Return only active users
    
    Returns: 200 OK - List of users
    """
    if role:
        users = get_users_by_role(db, role, skip=skip, limit=limit)
    elif active_only:
        users = get_active_users(db, skip=skip, limit=limit)
    else:
        users = get_users_paginated(db, skip=skip, limit=limit)
    
    return users


@router.get("/admin/users/{user_id}", response_model=UserInDB)
async def get_user_by_id_admin(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get user by ID with full details (Admin only).
    
    Returns complete user data including sensitive information.
    Returns: 200 OK - User found
    Returns: 404 Not Found - User not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/admin/users/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,
    user_data: UserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Update any user (Admin only).
    - Admins can update any user's profile
    - Validates unique constraints
    - Only updates provided fields
    Returns: 200 OK - User updated successfully
    Returns: 404 Not Found - User not found
    """
    updated_user = update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.patch("/admin/users/{user_id}", response_model=UserOut)
async def partial_update_user_admin(
    user_id: int,
    user_data: UserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Partially update any user (Admin only).
    Same as PUT but semantically indicates partial updates.
    Returns: 200 OK - User updated successfully
    Returns: 404 Not Found - User not found
    """
    updated_user = update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.post("/admin/users/{user_id}/activate")
async def activate_user_admin(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Activate a user account (Admin only).
    - Sets is_active to True
    - Clears disabled_at timestamp
    Returns: 200 OK - User activated successfully
    Returns: 404 Not Found - User not found
    """
    success = activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User activated successfully"}


@router.post("/admin/users/{user_id}/deactivate")
async def deactivate_user_admin(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account (Admin only).
    - Sets is_active to False
    - Records deactivation timestamp
    
    Returns: 200 OK - User deactivated successfully
    Returns: 404 Not Found - User not found
    """
    success = deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deactivated successfully"}


@router.post("/admin/users/bulk-status")
async def bulk_update_user_status_admin(
    user_ids: List[int],
    is_active: bool,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Bulk activate/deactivate users (Admin only).
    
    Updates multiple users' active status at once.
    
    Returns: 200 OK - Bulk operation completed
    """
    updated_count = bulk_update_user_status(db, user_ids, is_active)
    action = "activated" if is_active else "deactivated"
    return {
        "message": f"Successfully {action} {updated_count} users",
        "updated_count": updated_count
    }


@router.get("/admin/users/{user_id}/audit-logs")
async def get_user_audit_logs_admin(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return")
):
    """
    Get user's audit logs (Admin only).
    Returns paginated list of user's audit log entries.
    Returns: 200 OK - List of audit logs
    """
    audit_logs = get_user_audit_logs(db, user_id, skip=skip, limit=limit)
    return {
        "audit_logs": audit_logs,
        "total": len(audit_logs),
        "skip": skip,
        "limit": limit
    }


@router.get("/admin/statistics")
async def get_user_statistics_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get user statistics (Admin only).
    
    Returns user counts by role and active user count.
    Returns: 200 OK - User statistics
    """
    role_counts = get_user_count_by_role(db)
    active_count = get_active_user_count(db)
    
    return {
        "role_counts": role_counts,
        "active_users": active_count,
        "total_users": sum(role_counts.values())
    } 
