from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Boolean, Text, Index
from app.db.base_class import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)# Primary Key
    # Token Info
    token = Column(Text, nullable=False, unique=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False) # Expiration
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # Table-level constraints
    __table_args__ = (
        Index("idx_refresh_token_user", "user_id"),
        Index("idx_refresh_token_expires", "expires_at"),
        Index("idx_refresh_token_revoked", "is_revoked"),
    )

    def __repr__(self):
        return f"<RefreshToken id={self.id} user_id={self.user_id} revoked={self.is_revoked}>" 
