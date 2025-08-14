from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class EmailVerificationToken(Base):
    """Model for email verification tokens"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    token_type = Column(String(50), default="email_verification")  # email_verification, password_reset
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="email_verification_tokens")

    def is_expired(self) -> bool:
        """Check if token is expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at

    def is_used(self) -> bool:
        """Check if token has been used"""
        return self.used_at is not None

    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)"""
        return not self.is_expired() and not self.is_used()
