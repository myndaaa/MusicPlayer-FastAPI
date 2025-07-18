
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean,Index, UniqueConstraint
from app.db.base import Base


class Band(Base):
    __tablename__ = "band"

    # Primary Key
    band_id = Column(Integer, primary_key=True, autoincrement=True)

    # Band Info
    name = Column(String(50), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    social_link = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    is_disabled = Column(Boolean, default=False, nullable=False)
    disabled_at = Column(DateTime, nullable=True)

    # constraints and indexes
    __table_args__ = (
        UniqueConstraint("name", name="uq_band_name"),
        Index("ix_band_name", "name"),
    )

    def __repr__(self):
        return f"<Band id={self.band_id} name={self.name} disabled={self.is_disabled}>"
