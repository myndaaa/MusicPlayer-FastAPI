from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserRole
from app.services.auth import AuthService
from app.crud.user import get_user_by_id

# HTTP Bearer token scheme for JWT authentication
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], 
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates the current user from JWT access token.
    - Validates the JWT access token
    - Extracts user information from token
    - Fetches the complete user object from database
    - Returns the authenticated user
    
    Args:
        credentials: HTTP Bearer token credentials from Authorization header
        db: Database session for user lookup
    Returns:
        User: Complete user object from database
    Raises:
        HTTPException (401): If token is invalid, expired, or user not found
        HTTPException (401): If authentication credentials are malformed
    """
    auth_service = AuthService(db)
    
    try:
        # Validate access token and extract user data
        token_data = auth_service.validate_access_token(credentials.credentials)
        
        # Get complete user object from database
        user_id = int(token_data.user_id)
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
        
    except HTTPException:
        # Raise HTTP exceptions (like token validation errors)
        raise
    except Exception:
        # Catch any other exceptions and return generic auth error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Validates that the current user is active and not disabled.
    - Ensures user account is active (is_active = True)
    - Ensures user account is not disabled (disabled_at = None)
    - Used for most authenticated endpoints
    Args:
        current_user: User object from get_current_user dependency
    Returns:
        User: Active and enabled user object
        
    Raises:
        HTTPException (403): If user account is inactive or disabled
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    if current_user.disabled_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been disabled"
        )
    return current_user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Validates that the current user has admin role.
    This dependency ensures the user has admin privileges:
    - Requires user to be authenticated and active
    - Checks if user role is 'admin'
    - Used for admin-only endpoints
    Args:
        current_user: Active user object from get_current_active_user
    Returns:
        User: Admin user object
    Raises:
        HTTPException (403): If user is not an admin
    """
    if current_user.role != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_musician(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Validates that the current user has musician role.
    - Requires user to be authenticated and active
    - Checks if user role is 'musician'
    - Used for musician-only endpoints (upload music, manage artist profile)
    Args:
        current_user: Active user object from get_current_active_user
    Returns:
        User: Musician user object
    Raises:
        HTTPException (403): If user is not a musician
    """
    if current_user.role != UserRole.musician.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Musician access required"
        )
    return current_user


def get_current_listener(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Validates that the current user has listener role.
    
    This dependency ensures the user has listener privileges:
    - Requires user to be authenticated and active
    - Checks if user role is 'listener'
    - Used for listener-only endpoints (basic music features)
    
    Args:
        current_user: Active user object from get_current_active_user
    Returns:
        User: Listener user object
    Raises:
        HTTPException (403): If user is not a listener
    """
    if current_user.role != UserRole.listener.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Listener access required"
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[Annotated[HTTPAuthorizationCredentials, Depends(security)]] = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Extracts current user if token is provided, otherwise returns None.
    This dependency is useful for endpoints that work both for:
    - Authenticated users (with token)
    - Anonymous users (without token)
    Examples: Public user profiles, search endpoints
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session for user lookup
        
    Returns:
        User or None: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        # Return None instead of raising exception for optional auth
        return None


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Provides an AuthService instance for dependency injection.
    This dependency provides access to the authentication service
    for token management, validation, and cleanup operations.
    
    Args:
        db: Database session for AuthService
        
    Returns:
        AuthService: Authentication service instance
    """
    return AuthService(db) 
