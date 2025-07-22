from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Following(Base):
    __tablename__ = "followings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=True)
    band_id = Column(Integer, ForeignKey("bands.id", ondelete="CASCADE"), nullable=True)

    started_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="followings", lazy="select")
    artist = relationship("Artist", back_populates="followers", lazy="select")
    band = relationship("Band", back_populates="followers", lazy="select")


    # Indexes
    __table_args__ = (
        Index("idx_followings_user_id", "user_id"),
        Index("idx_followings_artist_id", "artist_id"),
        Index("idx_followings_band_id", "band_id"),
        UniqueConstraint("user_id", "artist_id", name="uq_user_artist_follow"),
        UniqueConstraint("user_id", "band_id", name="uq_user_band_follow"),
    )

    def __repr__(self):
        return (
            f"<Following id={self.id} user_id={self.user_id} "
            f"artist_id={self.artist_id} band_id={self.band_id} started_at={self.started_at}>"
        )
