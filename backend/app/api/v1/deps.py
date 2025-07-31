from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserRole
from app.services.auth import AuthService
from app.crud.user import get_user_by_id

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)) -> User:
    """
    Extracts and validates the current user from JWT token.
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
    Returns:
        User: Current authenticated user
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    auth_service = AuthService(db)
    
    try:
        # validate access token
        token_data = auth_service.validate_access_token(credentials.credentials)
        
        # get user from database
        user_id = int(token_data.user_id)
        user = get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Validates that the current user is active and not disabled.
    Args:
        current_user: Current authenticated user
    Returns:
        User: Active user
    Raises:
        HTTPException: If user is inactive or disabled
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


def get_current_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """
    Validates that the current user has admin role.
    Args:
        current_user: Current active user
    Returns:
        User: Admin user 
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


def get_current_musician_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    """
    Validates that the current user has musician role.
    Args:
        current_user: Current active user 
    Returns:
        User: Musician user
    Raises:
        HTTPException: If user is not a musician
    """
    if current_user.role != UserRole.musician.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Musician access required"
        )
    return current_user


def get_current_user_or_optional(credentials: Optional[Annotated[HTTPAuthorizationCredentials, Depends(security)]] = None,db: Session = Depends(get_db)) -> Optional[User]:
    """
    Extracts current user if token is provided, otherwise returns None.
    Useful for endpoints that work both for authenticated and anonymous users.
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session
    Returns:
        User or None: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def require_user_role(required_role: UserRole):
    """
    Dependency for role-based access control.
    Args:
        required_role: Role required to access the endpoint
    Returns:
        Dependency function that validates user has required role
    """
    def role_validator(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        """
        Validates that the current user has the required role.
        Args:
            current_user: Current active user
        Returns:
            User: User with required role
        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.value.title()} access required"
            )
        
        return current_user
    
    return role_validator


# Convenience dependencies for common roles
get_current_admin = require_user_role(UserRole.admin)
get_current_musician = require_user_role(UserRole.musician)
get_current_user_role = require_user_role(UserRole.listener)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Provides an AuthService instance for dependency injection.
    Args:
        db: Database session
    Returns:
        AuthService: Authentication service instance
    """
    return AuthService(db) 
