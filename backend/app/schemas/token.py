from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict


class Token(BaseModel):
    """Access token response schema - aligns with create_access_token()"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration


class TokenRefresh(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload schema - aligns with security.py JWT functions"""
    sub: str  # user_id as string (from create_access_token)
    exp: datetime  # expiration time
    iat: datetime  # issued at time
    type: str  # "access" or "refresh"
    username: Optional[str] = None  # from create_access_token
    email: Optional[str] = None  # from create_access_token
    role: Optional[str] = None  # from create_access_token

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    """Token data for internal use after decoding"""
    user_id: Optional[str] = None  # sub field from JWT
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    token_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RefreshToken(BaseModel):
    """Refresh token schema for database storage"""
    token: str
    user_id: str  # matches sub field from JWT
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class TokenCreate(BaseModel):
    """Schema for creating tokens - aligns with security.py functions"""
    subject: str  # user_id
    username: str
    email: str
    role: str
    expires_delta: Optional[timedelta] = None
    additional_claims: Optional[Dict[str, Any]] = None


class RefreshTokenCreate(BaseModel):
    """Schema for creating refresh tokens"""
    subject: str  # user_id
    expires_delta: Optional[timedelta] = None


class TokenResponse(BaseModel):
    """Complete token response including both access and refresh tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration
    user_id: str
    username: str
    email: str
    role: str


class TokenValidation(BaseModel):
    """Schema for token validation requests"""
    token: str
    token_type: str = "access"  


class TokenRevoke(BaseModel):
    """Schema for revoking refresh tokens"""
    refresh_token: str
    user_id: str

