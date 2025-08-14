from sqlalchemy.orm import Session
from app.db.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.services.token_service import TokenService
from app.services.email_service import EmailService
from datetime import datetime, timezone
from typing import Optional


class EmailCRUD:
    """CRUD operations for email verification"""
    
    @staticmethod
    def verify_email(db: Session, token: str) -> tuple[bool, str, Optional[User]]:
        """Verify email with token"""
        verification_token = TokenService.get_valid_token(db, token, "email_verification")
        if not verification_token:
            return False, "Invalid, expired, or already used verification token", None
        user = db.query(User).filter(User.id == verification_token.user_id).first()
        if not user:
            return False, "User not found", None
        if user.email_verified:
            return False, "Email is already verified", user
        TokenService.mark_token_as_used(db, verification_token)
        user.email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        
        TokenService.invalidate_user_tokens(db, user.id, "email_verification")
        
        db.commit()
        
        return True, "Email verified successfully", user
    
    @staticmethod
    async def resend_verification_email(db: Session, email: str) -> tuple[bool, str]:
        """Resend verification email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return True, "If the email exists, a verification link has been sent"
        if user.email_verified:
            return True, "Email is already verified"
        TokenService.invalidate_user_tokens(db, user.id, "email_verification")
        verification_token = TokenService.create_verification_token(
            db, user.id, "email_verification", 24
        )
        email_service = EmailService()
        success = await email_service.send_verification_email(user, verification_token.token)
        
        if success:
            return True, "Verification email sent successfully"
        else:
            return False, "Failed to send verification email"
    
    @staticmethod
    async def send_password_reset_email(db: Session, email: str) -> tuple[bool, str]:
        """Send password reset email"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return True, "If the email exists, a password reset link has been sent"
        TokenService.invalidate_user_tokens(db, user.id, "password_reset")
        reset_token = TokenService.create_verification_token(
            db, user.id, "password_reset", 1
        )
        email_service = EmailService()
        success = await email_service.send_password_reset_email(user, reset_token.token)
        
        if success:
            return True, "Password reset email sent successfully"
        else:
            return False, "Failed to send password reset email"
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> tuple[bool, str]:
        """Reset password with token"""
        reset_token = TokenService.get_valid_token(db, token, "password_reset")
        
        if not reset_token:
            return False, "Invalid, expired, or already used reset token"
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            return False, "User not found"
        TokenService.mark_token_as_used(db, reset_token)
        from app.core.security import get_password_hash
        user.password = get_password_hash(new_password)
        TokenService.invalidate_user_tokens(db, user.id, "password_reset")
        
        db.commit()
        
        return True, "Password reset successfully"
