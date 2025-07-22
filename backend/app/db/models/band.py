
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean,Index, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class Band(Base):
    __tablename__ = "bands"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Band Info
    name = Column(String(50), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    social_link = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    is_disabled = Column(Boolean, default=False, nullable=False)
    disabled_at = Column(DateTime, nullable=True)


    # Relationships
    
    songs = relationship("Song", back_populates="band", lazy="select")
    albums = relationship("Album", back_populates="band", lazy="select")
    artist_band_members = relationship("ArtistBandMember", back_populates="band", lazy="select")
    followers = relationship("Following", back_populates="band", lazy="select")
    followers = relationship("Following", back_populates="band", lazy="select", cascade="all, delete-orphan")


    # constraints and indexes
    __table_args__ = (
        UniqueConstraint("name", name="uq_band_name"),
        Index("ix_band_name", "name"),
    )

    def __repr__(self):
        return f"<Band id={self.band_id} name={self.name} disabled={self.is_disabled}>"
