import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.email_verification import EmailVerificationToken
from app.db.models.user import User


class TokenService:
    """Service for generating and managing email verification tokens"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_verification_token(
        db: Session, 
        user_id: int, 
        token_type: str = "email_verification",
        expires_in_hours: int = 24
    ) -> EmailVerificationToken:
        """Create a new verification token"""
        token = TokenService.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        
        verification_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
        
        db.add(verification_token)
        db.commit()
        db.refresh(verification_token)
        
        return verification_token
    
    @staticmethod
    def get_token_by_value(db: Session, token: str) -> Optional[EmailVerificationToken]:
        """Get token by its value"""
        return db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token
        ).first()
    
    @staticmethod
    def get_valid_token(db: Session, token: str, token_type: str = "email_verification") -> Optional[EmailVerificationToken]:
        """Get a valid token (not expired, not used)"""
        verification_token = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token,
            EmailVerificationToken.token_type == token_type
        ).first()
        
        if verification_token and verification_token.is_valid():
            return verification_token
        
        return None
    
    @staticmethod
    def mark_token_as_used(db: Session, token: EmailVerificationToken) -> None:
        """Mark a token as used"""
        token.used_at = datetime.now(timezone.utc)
        db.commit()
    
    @staticmethod
    def invalidate_user_tokens(db: Session, user_id: int, token_type: str = "email_verification") -> None:
        """Invalidate all tokens of a specific type for a user"""
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.token_type == token_type,
            EmailVerificationToken.used_at.is_(None)
        ).update({"used_at": datetime.now(timezone.utc)})
        db.commit()
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Clean up expired tokens and return count of deleted tokens"""
        expired_tokens = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.expires_at < datetime.now(timezone.utc)
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        return count
