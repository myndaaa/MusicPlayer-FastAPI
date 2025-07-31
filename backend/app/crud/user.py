from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate, UserRole
from app.core.security import hash_password, verify_password



def create_user(db: Session, user_data: UserCreate) -> User:
    """
    This function handles the complete user creation process:
    - Hashes the password securely using Argon2id
    - Checks for unique username and email constraints
    - Sets default values and timestamps
    - Returns the created user object
    Args:
        db: Database session for the operation
        user_data: User data containing username, email, password, etc.
    Returns:
        User: The newly created user object with hashed password 
    Raises:
        IntegrityError: If username or email already exists
    """
    # hash the password before storing it
    hashed_password = hash_password(user_data.password)
    
    # create user object with hashed password
    db_user = User(
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role.value,  # convert enum to string
        created_at=datetime.now(timezone.utc),
        is_active=True
    )
    
    # save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by their unique ID.
    Args:
        db: Database session
        user_id: The unique identifier of the user
    Returns:
        User or None: The user object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Finds a user by their username.
    Args:
        db: Database session
        username: The username to search for
    Returns:
        User or None: The user object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Finds a user by their email address.
    Args:
        db: Database session
        email: The email address to search for
    Returns:
        User or None: The user object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Updates user information in the database.
    Args:
        db: Database session
        user_id: ID of the user to update
        user_data: New user data (only provided fields will be updated)
    Returns:
        User or None: Updated user object if successful, None if user not found
    Raises:
        IntegrityError: If new username or email conflicts with existing users
    """
    # get the user first
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    # update only the fields that were provided
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # commit
    db.commit()
    db.refresh(db_user)
    
    return db_user


def change_password(db: Session, user_id: int, password_data: UserPasswordUpdate) -> bool:
    """
    Changes a user's password after verifying the old one.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    # verify old password first
    if not verify_password(password_data.old_password, user.password):
        return False
    
    # hash and update new password (schema already validated the new password)
    hashed_new_password = hash_password(password_data.new_password)
    user.password = hashed_new_password
    db.commit()
    return True


def reset_password_request(db: Session, email: str) -> bool:
    """
    Initiates a password reset process for a user.
    - Finds the user by email
    - Generates a reset token (implementation needed)
    - Would send an email with reset link (future feature)
    - Returns success status
    Args:
        db: Database session
        email: Email address of the user requesting reset
        
    Returns:
        bool: True if reset request was processed, False if user not found
    """
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return False
    
    # TODO: generate reset token and send email 
    return True


def reset_password_confirm(db: Session, token: str, new_password: str) -> bool:
    """
    Confirms password reset using a valid token.
    - Validates the reset token
    - Updates the user's password if token is valid
    - Invalidates the token after use
    Args:
        db: Database session
        token: Password reset token
        new_password: New password to set
        
    Returns:
        bool: True if password was reset successfully, False if token invalid
    """
    # TODO: implement token validation logic
    # for now, return False
    return False


def activate_user(db: Session, user_id: int) -> bool:
    """
    Reactivates a previously deactivated user.
    - Sets is_active to True
    - Clears the disabled_at timestamp
    - Allows the user to log in again
    Args:
        db: Database session
        user_id: ID of the user to activate
        
    Returns:
        bool: True if user was activated, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = True
    user.disabled_at = None
    
    db.commit()
    return True


def deactivate_user(db: Session, user_id: int) -> bool:
    """
    Deactivates a user account.
    - Sets is_active to False
    - Records the deactivation timestamp
    - Prevents user from logging in  
    Args:
        db: Database session
        user_id: ID of the user to deactivate    
    Returns:
        bool: True if user was deactivated, False if not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    user.disabled_at = datetime.now(timezone.utc)
    
    db.commit()
    return True



def get_users_paginated(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves a paginated list of users.
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List[User]: List of user objects
    """
    return db.query(User).offset(skip).limit(limit).all()


def search_users_by_name(db: Session, name: str) -> List[User]:
    """
    Searches for users by their first or last name.
    Args:
        db: Database session
        name: Name to search for (can be partial)
    Returns:
        List[User]: List of users matching the name search
    """
    search_term = f"%{name}%"
    return db.query(User).filter(
        or_(
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term)
        )
    ).all()


def get_users_by_role(db: Session, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves all users with a specific role.
    Useful for role-based operations like finding all admins
    or all musicians in the system.
    Args:
        db: Database session
        role: The role to filter by (admin, user, musician)
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    Returns:
        List[User]: List of users with the specified role
    """
    return db.query(User).filter(User.role == role.value).offset(skip).limit(limit).all()


def get_active_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves all active users in the system.
    This function returns only users who can currently
    log in and use the application.
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    Returns:
        List[User]: List of active users
    """
    return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


def get_inactive_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Retrieves all inactive users in the system.
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    Returns:
        List[User]: List of inactive users
    """
    return db.query(User).filter(User.is_active == False).offset(skip).limit(limit).all()


def get_user_with_relationships(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user with all their related data.
    This function loads the user along with all their relationships
    like playlists, likes, history, etc. Useful for detailed
    user profiles or admin views.
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        User or None: User with all relationships loaded
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_playlists(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List:
    """
    Retrieves all playlists owned by a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    Returns:
        List: List of playlists owned by the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.playlists[skip:skip + limit]


def get_user_likes(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List:
    """
    Retrieves all songs liked by a user.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List: List of songs liked by the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.likes[skip:skip + limit]


def get_user_history(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List:
    """
    Retrieves the listening history of a user.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    Returns:
        List: List of history entries for the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.history[skip:skip + limit]


def get_user_subscriptions(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List:
    """
    Retrieves all subscription records for a user.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List: List of subscription records for the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.subscriptions[skip:skip + limit]


def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List:
    """
    Retrieves all payment records for a user.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List: List of payment records for the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.payments[skip:skip + limit]



def get_user_audit_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List:
    """
    Retrieves audit logs for a specific user.
    Returns all audit log entries related to
    actions performed by specified user.
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List: List of audit log entries for the user
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return []
    return user.audit_logs[skip:skip + limit]


def bulk_update_user_status(db: Session, user_ids: List[int], is_active: bool) -> int:
    """
    Bulk activates or deactivates multiple users.
    Only for admin.
    Args:
        db: Database session
        user_ids: List of user IDs to update
        is_active: True for active, False for inactive)
    Returns:
        int: Number of users successfully updated
    """
    result = db.query(User).filter(User.id.in_(user_ids)).update(
        {
            "is_active": is_active,
            "disabled_at": None if is_active else datetime.now(timezone.utc)
        },
        synchronize_session=False
    )
    db.commit()
    return result


def get_user_count_by_role(db: Session) -> Dict[str, int]:
    """
    Counts users by their role, provides statistics for dashboard displays
    and system analytics
    Args:
        db: Database session
    Returns:
        Dict[str, int]: Dictionary with role names as keys and counts as values
    """
    result = db.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    return {role: count for role, count in result}


def get_active_user_count(db: Session) -> int:
    """
    Counts the total number of active users.
    This function provides a quick metric for system health
    and user engagement.
    Args:
        db: Database session
    Returns:
        int: Total number of active users
    """
    return db.query(User).filter(User.is_active == True).count()

def update_last_login(db: Session, user_id: int) -> bool:
    """
    Updates the user's last login timestamp.
    Called after successful authentication
    to track user activity and session management.
    Args:
        db: Database session
        user_id: ID of the user
    Returns:
        bool: True if updated successfully, False if user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return True


def validate_user_role(db: Session, user_id: int, required_role: UserRole) -> bool:
    """
    Validates if a user has the required role.
    Will use on auth module.
    Args:
        db: Database session
        user_id: ID of the user to check
        required_role: Role that the user must have
    Returns:
        bool: True if user has the required role, False otherwise
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    return user.role == required_role.value
