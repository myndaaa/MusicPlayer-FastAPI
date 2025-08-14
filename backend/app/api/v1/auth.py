from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserLogin, UserOut
from app.schemas.token import TokenResponse, TokenRefresh
from app.services.auth import AuthService
from app.core.deps import get_current_active_user, get_current_admin, get_auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access/refresh tokens.
    - Validates username and password
    - Checks if user account is active
    - Creates access and refresh tokens
    - Stores refresh token in database for revocation
    - Updates user's last login timestamp
    """
    auth_service = AuthService(db)
    
    # authenticate user
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check email verification
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email and click the verification link."
        )
    
    # create tokens
    token_response = auth_service.create_tokens(user)
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    - Validates the refresh token
    - Checks if token is revoked in database
    - Creates new access token
    - Keeps the same refresh token
    """
    auth_service = AuthService(db)
    
    try:
        token_response = auth_service.refresh_access_token(refresh_data.refresh_token)
        return token_response
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/logout")
async def logout(
    refresh_data: TokenRefresh,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking their refresh token.
    - Validates the refresh token belongs to current user
    - Marks the refresh token as revoked in database
    - Records revocation timestamp
    """
    auth_service = AuthService(db)
    success = auth_service.logout(refresh_data.refresh_token, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Logout user from all sessions by revoking all their refresh tokens.
    - Finds all active refresh tokens for the user
    - Revokes all tokens
    - Useful for security (password change, suspicious activity)
    """
    auth_service = AuthService(db)
    revoked_count = auth_service.logout_all_sessions(current_user.id)
    
    return {
        "message": f"Successfully logged out from {revoked_count} sessions",
        "sessions_revoked": revoked_count
    }


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user information.
    - Returns current user's profile information
    - Validates that user is active and authenticated
    """
    return current_user

'''

TODO: use cron job -- refer to issues for assistance

@router.post("/cleanup-expired")
async def cleanup_expired_tokens(
    current_admin: Annotated[User, Depends(get_current_admin)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """
    Clean up expired refresh tokens from database (Admin only).
    - Removes expired refresh tokens
    - Helps maintain database performance
    - Admin access required
    """
    cleaned_count = auth_service.cleanup_expired_tokens()
    return {
        "message": f"Cleaned up {cleaned_count} expired tokens",
        "tokens_removed": cleaned_count
    }
'''
