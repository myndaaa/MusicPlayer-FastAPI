import secrets
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.core.utils import utc_now, EMAIL_VERIFICATION_TOKEN_HOURS
from app.db.models.email_verification import EmailVerificationToken


class TokenService:
    """Service for generating and managing verification/reset tokens."""

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_token(
        db: Session,
        user_id: int,
        token_type: str = "email_verification",
        expires_in_hours: Optional[int] = None,
    ) -> EmailVerificationToken:
        if expires_in_hours is None:
            expires_in_hours = EMAIL_VERIFICATION_TOKEN_HOURS

        token_value = TokenService.generate_token()
        expires_at = utc_now() + timedelta(hours=expires_in_hours)

        token = EmailVerificationToken(
            user_id=user_id,
            token=token_value,
            token_type=token_type,
            expires_at=expires_at,
        )

        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_token_by_value(db: Session, token: str) -> Optional[EmailVerificationToken]:
        return db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()

    @staticmethod
    def get_valid_token(db: Session, token: str, token_type: str = "email_verification") -> Optional[EmailVerificationToken]:
        token_obj = (
            db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.token == token,
                EmailVerificationToken.token_type == token_type,
            )
            .first()
        )
        if token_obj and token_obj.is_valid():
            return token_obj
        return None

    @staticmethod
    def mark_token_as_used(db: Session, token_obj: EmailVerificationToken) -> None:
        token_obj.used_at = utc_now()
        db.commit()

    @staticmethod
    def invalidate_user_tokens(db: Session, user_id: int, token_type: str = "email_verification") -> None:
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.token_type == token_type,
            EmailVerificationToken.used_at.is_(None),
        ).update({"used_at": utc_now()})
        db.commit()

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        expired = db.query(EmailVerificationToken).filter(EmailVerificationToken.expires_at < utc_now()).all()
        count = len(expired)
        for t in expired:
            db.delete(t)
        db.commit()
        return count


