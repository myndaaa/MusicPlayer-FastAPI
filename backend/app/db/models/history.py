from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    played_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="history", lazy="select")
    song = relationship("Song", back_populates="histories", lazy="select")

    __table_args__ = (
        Index("idx_history_user_song", "user_id", "song_id"),
    )

    def __repr__(self):
        return f"<History id={self.id} user_id={self.user_id} song_id={self.song_id} played_at={self.played_at}>"

