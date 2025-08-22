from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.core.utils import utc_now
from app.services.token_service import TokenService
from app.services.email_service import EmailService


class EmailCRUD:
    """CRUD operations for email verification and password reset."""

    @staticmethod
    def verify_email(db: Session, token: str) -> Tuple[bool, str, Optional[User]]:
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
        user.email_verified_at = utc_now()
        TokenService.invalidate_user_tokens(db, user.id, "email_verification")
        db.commit()
        return True, "Email verified successfully", user

    @staticmethod
    def resend_verification_email(db: Session, email: str, email_service: EmailService) -> Tuple[bool, str]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return True, "If the email exists, a verification link has been sent"
        if user.email_verified:
            return True, "Email is already verified"

        TokenService.invalidate_user_tokens(db, user.id, "email_verification")
        verification_token = TokenService.create_token(db, user.id, "email_verification")
        success = email_service.send_verification_email(user, verification_token.token)
        if success:
            return True, "Verification email sent successfully"
        return False, "Failed to send verification email"


