
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import JSONB  
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Artist(Base):
    __tablename__ = "artists"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Artist Info
    artist_stage_name = Column(String(50), nullable=False)
    artist_bio = Column(Text, nullable=True)
    artist_profile_image = Column(String(255), nullable=True)  # Store S3/Cloud URL
    artist_social_link = Column(JSON, nullable=True)  
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    linked_user_account = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # FK to User 
    is_disabled = Column(Boolean, default=False, nullable=False)  
    disabled_at = Column(DateTime, nullable=True)  

   
    # Relationships
    linked_user = relationship("User", back_populates="artist_profile", lazy="select", uselist=False)
    songs = relationship("Song", back_populates="artist", lazy="select")
    albums = relationship("Album", back_populates="artist", lazy="select")
    band_memberships = relationship("ArtistBandMember", back_populates="artist", lazy="select")
    followers = relationship("Following", back_populates="artist", lazy="select", cascade="all, delete-orphan")




    # Constraints n Indexes
    __table_args__ = (
        UniqueConstraint("linked_user_account", name="uq_artist_user_account"),
        Index("idx_artist_stage_name", "artist_stage_name"),
    )

    # For debugging
    def __repr__(self):
        return f"<Artist id={self.id} stage_name={self.artist_stage_name}>"
