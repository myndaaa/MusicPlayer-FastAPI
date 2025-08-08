from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.schemas.user import UserLogin
from app.schemas.token import TokenResponse, TokenData
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token
)
from app.crud.user import get_user_by_username, get_user_by_id, update_last_login


class AuthService:
    """
    Authentication service handling login, token management, and logout.
    """
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticates a user with username and password.
        Args:
            login_data: User login credentials
        Returns:
            User object if authentication successful, else None 
        Raises:
            HTTPException: If user is inactive or authentication fails
        """
        # find user by username
        user = get_user_by_username(self.db, login_data.username)
        if not user:
            return None
        # check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        # verify password
        if not verify_password(login_data.password, user.password):
            return None
        # update last login time
        update_last_login(self.db, user.id)
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        """
        Creates access and refresh tokens for a user.
        Args:
            user: Authenticated user object
        Returns:
            TokenResponse with both access and refresh tokens
        """
        # create access token
        access_token = create_access_token(
            subject=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role
        )
        # create refresh token
        refresh_token = create_refresh_token(subject=str(user.id))
        # store refresh token in database
        self._store_refresh_token(refresh_token, user.id)
        
        # decode access token to get expiration (now returns Unix timestamp)
        token_data = decode_token(access_token)
        current_time = int(datetime.now(timezone.utc).timestamp())
        expires_in = token_data["exp"] - current_time
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Refreshes an access token using a valid refresh token.
        Creates new refresh token on each use.
        Args:
            refresh_token: Valid refresh token
        Returns:
            TokenResponse with new access token and rotated refresh token
        Raises:
            HTTPException: If refresh token is invalid, expired, revoked/rotated
        """
        # decode and validate refresh token
        try:
            token_data = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        # check if its a refresh token
        if token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        # check if token is revoked/rotated in database
        db_token = self._get_refresh_token(refresh_token)
        if not db_token or db_token.is_revoked or db_token.is_rotated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or rotated"
            )
        # check if token has expired
        if datetime.now(timezone.utc) > db_token.expires_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        # get user
        user_id = int(token_data["sub"])
        user = get_user_by_id(self.db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        # create new access token
        new_access_token = create_access_token(
            subject=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role
        )
        # create new refresh token for rotation 
        new_refresh_token = create_refresh_token(subject=str(user.id))
        # mark old token as rotated
        db_token.is_rotated = True
        db_token.rotated_at = datetime.now(timezone.utc)
        # store new refresh token with link to previous
        new_db_token = self._store_refresh_token(new_refresh_token, user.id, db_token.id)
        # decode to get expiration
        new_token_data = decode_token(new_access_token)
        # Calculate expiration using Unix timestamps
        current_time = int(datetime.now(timezone.utc).timestamp())
        expires_in = new_token_data["exp"] - current_time
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,  # new rotated refresh token
            token_type="bearer",
            expires_in=expires_in,
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role
        )

    def logout(self, refresh_token: str, user_id: int) -> bool:
        """
        Logs out a user by revoking their refresh token.
        Args:
            refresh_token: Refresh token to revoke
            user_id: ID of the user logging out
        Returns:
            True if logout successful, False otherwise
        """
        # find and revoke the refresh token
        db_token = self._get_refresh_token(refresh_token)
        if db_token and db_token.user_id == user_id:
            db_token.is_revoked = True
            db_token.revoked_at = datetime.now(timezone.utc)
            self.db.commit()
            return True
        return False

    def logout_all_sessions(self, user_id: int) -> int:
        """
        Logs out user from all sessions by revoking all their refresh tokens.
        Args:
            user_id: ID of the user
        Returns:
            Number of sessions revoked
        """
        # find all active refresh tokens for user [not revoked, not rotated, not expired]
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
            RefreshToken.is_rotated == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).all()
        
        # revoke all tokens
        revoked_count = 0
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            revoked_count += 1
        
        self.db.commit()
        return revoked_count

    def validate_access_token(self, token: str) -> TokenData:
        """
        Validates an access token and returns token data.
        Args:
            token: Access token to validate
        Returns:
            TokenData with user information
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            token_data = decode_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # check if it's an access token
        if token_data.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return TokenData(
            user_id=token_data.get("sub"),
            username=token_data.get("username"),
            email=token_data.get("email"),
            role=token_data.get("role"),
            token_type=token_data.get("type")
        )

    def _store_refresh_token(self, token: str, user_id: int, previous_token_id: Optional[int] = None) -> RefreshToken:
        """
        Stores a refresh token in the database.
        Args:
            token: Refresh token string
            user_id: ID of the user
            previous_token_id: ID of the previous token in rotation chain (optional)
        Returns:
            RefreshToken object
        """
        # decode token to get expiration (Unix timestamp)
        token_data = decode_token(token)
        # Convert Unix timestamp to datetime for database storage
        expires_at = datetime.fromtimestamp(token_data["exp"], tz=timezone.utc)
        
        # create database record
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            is_revoked=False,
            is_rotated=False,
            previous_token_id=previous_token_id
        )
        
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        
        return db_token

    def _get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """
        Retrieves a refresh token from the database.
        Args:
            token: Refresh token string 
        Returns:
            RefreshToken object if found, None otherwise
        """
        return self.db.query(RefreshToken).filter(RefreshToken.token == token).first()

    def cleanup_expired_tokens(self) -> int:
        """
        Removes expired and rotated refresh tokens from the database.
        Returns:
            Number of tokens removed
        """
        # remove expired tokens
        expired_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        ).all()
        
        # remove old rotated tokens (keep recent ones for audit)
        old_rotated_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.is_rotated == True,
            RefreshToken.rotated_at < datetime.now(timezone.utc) - timedelta(days=7)  # keep for 7 days
        ).all()
        
        tokens_to_delete = expired_tokens + old_rotated_tokens
        count = len(tokens_to_delete)
        
        for token in tokens_to_delete:
            self.db.delete(token)
        
        self.db.commit()
        return count

    def get_token_rotation_history(self, user_id: int, limit: int = 10) -> List[RefreshToken]:
        """
        Gets the token rotation history for a user.
        Useful for security auditing and detecting suspicious activity.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of tokens to return
            
        Returns:
            List of refresh tokens with rotation information
        """
        return self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).order_by(RefreshToken.created_at.desc()).limit(limit).all() 
