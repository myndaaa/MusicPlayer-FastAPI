
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Index, UniqueConstraint
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class ArtistBandMember(Base):
    __tablename__ = "artist_band_members"

    # Primary Key
    band_member_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    band_id = Column(Integer, ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    joined_on = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    left_at = Column(DateTime, nullable=True)
    is_current_member = Column(Boolean, default=True, nullable=False)


    # Relationships
    
    artist = relationship("Artist", back_populates="band_memberships", lazy="select")
    band = relationship("Band", back_populates="artist_members", lazy="select")


    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint("artist_id", "band_id", "joined_on", name="uq_artist_band_joined"),
        Index("idx_artist_band", "artist_id", "band_id"),
    )

    def __repr__(self):
        return (
            f"<ArtistBandMember id={self.band_member_id} "
            f"artist_id={self.artist_id} band_id={self.band_id} "
            f"current={self.is_current_member}>"
        )
