from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Following(Base):
    __tablename__ = "following"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artist.id", ondelete="CASCADE"), nullable=True)
    band_id = Column(Integer, ForeignKey("band.id", ondelete="CASCADE"), nullable=True)

    started_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="followings", lazy="select")
    artist = relationship("Artist", back_populates="followers", lazy="select")
    band = relationship("Band", back_populates="followers", lazy="select")

    def __repr__(self):
        return (
            f"<Following id={self.id} user_id={self.user_id} "
            f"artist_id={self.artist_id} band_id={self.band_id} started_at={self.started_at}>"
        )
