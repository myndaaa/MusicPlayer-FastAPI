from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailVerificationRequest(BaseModel):
    """Request schema for email verification"""
    token: str


class EmailVerificationResponse(BaseModel):
    """Response schema for email verification"""
    message: str
    user_id: Optional[int] = None
    email: Optional[str] = None


class ResendVerificationRequest(BaseModel):
    """Request schema for resending verification email"""
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    """Response schema for resending verification email"""
    message: str


class ForgotPasswordRequest(BaseModel):
    """Request schema for forgot password"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Response schema for forgot password"""
    message: str


class ResetPasswordRequest(BaseModel):
    """Request schema for password reset"""
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    """Response schema for password reset"""
    message: str
