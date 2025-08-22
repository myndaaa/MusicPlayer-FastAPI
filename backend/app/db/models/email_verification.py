from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from datetime import datetime, timezone


class EmailVerificationToken(Base):
    """Model for email verification and password reset tokens"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    token_type = Column(String(50), default="email_verification", nullable=False)  # email_verification, password_reset
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship with User model
    user = relationship("User", back_populates="email_verification_tokens")

    __table_args__ = (
        Index('idx_user_token_type', 'user_id', 'token_type'),
        Index('idx_expires_at', 'expires_at'),
    )

    def is_expired(self) -> bool:
        """Check if token is expired using timezone-aware datetime"""
        return datetime.now(timezone.utc) > self.expires_at

    def is_used(self) -> bool:
        """Check if token has been used"""
        return self.used_at is not None

    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)"""
        return not self.is_expired() and not self.is_used()

    def mark_as_used(self) -> None:
        """Mark token as used with current timestamp"""
        self.used_at = datetime.now(timezone.utc)
