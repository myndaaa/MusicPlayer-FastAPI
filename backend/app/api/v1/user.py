from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserPasswordUpdate, UserOut, UserRole,
    UserLogin, UserInDB, UserSignupBase
)
from app.crud.user import (
    create_user, get_user_by_id, get_user_by_username, get_user_by_email,
    update_user, change_password, activate_user, deactivate_user,
    get_users_paginated, search_users_by_name, get_users_by_role,
    get_active_users, get_inactive_users, get_user_with_relationships,
    get_user_playlists, get_user_likes, get_user_history,
    get_user_subscriptions, get_user_payments, get_user_audit_logs,
    bulk_update_user_status, get_user_count_by_role, get_active_user_count,
    update_last_login, validate_user_role
)
from app.api.v1.deps import (
    get_current_active_user, get_current_admin, get_current_listener_user,
    get_current_musician_user, get_current_user_or_optional,
    get_current_admin_user, get_current_musician_user, get_current_listener_user
)

router = APIRouter()


@router.post("/signup/listener", response_model=UserOut)
async def signup_listener(user_data: UserSignupBase, db: Session = Depends(get_db)):
    """
    Sign up a new listener user.
    - Validates user data and password strength
    - Checks for unique username and email
    - Automatically sets role to 'listener'
    - Creates active user account
    """
    # Create UserCreate object with role set to listener
    user_create_data = UserCreate(
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password=user_data.password,
        role=UserRole.listener
    )
    
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        user = create_user(db, user_create_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user account"
        )


@router.post("/signup/musician", response_model=UserOut)
async def signup_musician(user_data: UserCreate,db: Session = Depends(get_db)):
    """
    Sign up a new musician user.
    """
    # Ensure role is set to musician
    user_data.role = UserRole.musician
    
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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


@router.post("/signup/admin", response_model=UserOut)
async def signup_admin(
    user_data: UserCreate,current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)):
    """
    Create a new admin user (Admin only).
    """
    # Ensure role is set to admin
    user_data.role = UserRole.admin
    
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        user = create_user(db, user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create admin account"
        )


@router.get("/me/profile", response_model=UserOut)
async def get_my_profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Get current user's detailed profile information.
    Returns the authenticated user's complete profile data.
    Authentication: Any active user
    """
    return current_user


@router.put("/me", response_model=UserOut)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user's profile information.
    - Users can only update their own profile.
    - Validates unique constraints for username/email
    - Only updates provided fields
    - Cannot change role or sensitive fields
    """
    updated_user = update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.put("/me/password")
async def change_my_password(
    password_data: UserPasswordUpdate, current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    - Users can only change their own password.
    - Validates old password
    - Ensures new password meets strength requirements
    - Updates password hash
    """
    success = change_password(db, current_user.id, password_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )
    return {"message": "Password updated successfully"}



@router.get("/admin/all", response_model=List[UserOut])
async def get_all_users(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all users (Admin only).
    """
    users = get_users_paginated(db, skip=skip, limit=limit)
    return users


@router.get("/admin/counts")
async def get_user_counts( current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get user statistics (Admin only).
    """
    role_counts = get_user_count_by_role(db)
    active_count = get_active_user_count(db)
    
    return {
        "role_counts": role_counts,
        "active_users": active_count,
        "total_users": sum(role_counts.values())
    }


@router.get("/admin/active", response_model=List[UserOut])
async def get_active_users_admin(
    current_admin: Annotated[User, Depends(get_current_admin)], db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all active users (Admin only).
    """
    users = get_active_users(db, skip=skip, limit=limit)
    return users


@router.get("/admin/inactive", response_model=List[UserOut])
async def get_inactive_users_admin(
    current_admin: Annotated[User, Depends(get_current_admin)],db: Session = Depends(get_db),
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all inactive users (Admin only).
    """
    users = get_inactive_users(db, skip=skip, limit=limit)
    return users


@router.get("/admin/{user_id}", response_model=UserInDB)
async def get_user_by_id_admin(
    user_id: int,current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Get user by ID with full details (Admin only).
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/admin/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,user_data: UserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],db: Session = Depends(get_db)
):
    """
    Update any user (Admin only).
    """
    updated_user = update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.post("/admin/{user_id}/activate")
async def activate_user_admin(
    user_id: int, current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Activate a user account.
    """
    success = activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User activated successfully"}


@router.post("/me/deactivate")
async def deactivate_my_account(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Deactivate current user's own account.
    TODO: password confirmation (ask later in pr)
    """
    success = deactivate_user(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate account"
        )
    return {"message": "Account deactivated successfully"}


@router.post("/admin/{user_id}/deactivate")
async def deactivate_user_admin(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db)
):
    """
    Admins can deactivate any user account.
    - Can deactivate any user regardless of role
    - Can be reactivated by admin
    """
    success = deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deactivated successfully"}


@router.post("/admin/bulk-status")
async def bulk_update_user_status_admin(
    user_ids: List[int], is_active: bool,
    current_admin: Annotated[User, Depends(get_current_admin)],db: Session = Depends(get_db)
):
    """
    Bulk activate/deactivate users (Admin only).
    Updates multiple users' active status at once.
    """
    updated_count = bulk_update_user_status(db, user_ids, is_active)
    action = "activated" if is_active else "deactivated"
    return {
        "message": f"Successfully {action} {updated_count} users",
        "updated_count": updated_count
    }


@router.get("/search", response_model=List[UserOut])
async def search_users( current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db),name: str = Query(..., min_length=1)):
    """
    Search users by name.
    Searches for users by first name or last name.
    """
    users = search_users_by_name(db, name)
    return users


@router.get("/by-role/{role}", response_model=List[UserOut])
async def get_users_by_role_route(role: UserRole, current_admin: Annotated[User, Depends(get_current_admin)], db: Session = Depends(get_db), skip: int = Query(0, ge=0),limit: int = Query(100, ge=1, le=1000)):
    """
    Get users by role (Admin only).
    """
    users = get_users_by_role(db, role, skip=skip, limit=limit)
    return users



@router.get("/me/playlists")
async def get_my_playlists(
    current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db),skip: int = Query(0, ge=0),limit: int = Query(20, ge=1, le=100)
):
    """
    Get current user's playlists.
    """
    playlists = get_user_playlists(db, current_user.id, skip=skip, limit=limit)
    return {"playlists": playlists, "total": len(playlists)}


@router.get("/me/likes")
async def get_my_likes(current_user: Annotated[User, Depends(get_current_active_user)],db: Session = Depends(get_db),skip: int = Query(0, ge=0),limit: int = Query(50, ge=1, le=200)):
    """
    Get current user's liked songs.
    """
    likes = get_user_likes(db, current_user.id, skip=skip, limit=limit)
    return {"likes": likes, "total": len(likes)}


@router.get("/me/history")
async def get_my_history(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db),skip: int = Query(0, ge=0),limit: int = Query(100, ge=1, le=500)):
    """
    Get current user's listening history.
    """
    history = get_user_history(db, current_user.id, skip=skip, limit=limit)
    return {"history": history, "total": len(history)}


@router.get("/me/subscriptions")
async def get_my_subscriptions(current_user: Annotated[User, Depends(get_current_active_user)],db: Session = Depends(get_db),skip: int = Query(0, ge=0),limit: int = Query(50, ge=1, le=200)):
    """
    Get current user's subscriptions.
    """
    subscriptions = get_user_subscriptions(db, current_user.id, skip=skip, limit=limit)
    return {"subscriptions": subscriptions, "total": len(subscriptions)}


@router.get("/me/payments")
async def get_my_payments(current_user: Annotated[User, Depends(get_current_active_user)],db: Session = Depends(get_db),skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    """
    Get current user's payment history.
    """
    payments = get_user_payments(db, current_user.id, skip=skip, limit=limit)
    return {"payments": payments, "total": len(payments)}



@router.get("/admin/{user_id}/audit-logs")
async def get_user_audit_logs_admin( user_id: int, current_admin: Annotated[User, Depends(get_current_admin)], db: Session = Depends(get_db), skip: int = Query(0, ge=0),limit: int = Query(100, ge=1, le=500)
):
    """
    Get user's audit logs (Admin only).
    Returns paginated list of user's audit log entries.
    Authentication: Admin only
    """
    audit_logs = get_user_audit_logs(db, user_id, skip=skip, limit=limit)
    return {"audit_logs": audit_logs, "total": len(audit_logs)}



@router.get("/public/{user_id}", response_model=UserOut)
async def get_public_user_profile(user_id: int,current_user: Optional[User] = Depends(get_current_user_or_optional),db: Session = Depends(get_db)):
    """
    Get public user profile.
    """
    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If current user is viewing their own profile, return full data
    if current_user and current_user.id == user_id:
        return user
    
    # For public viewing, return limited data
    return UserOut(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    ) 
