from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    liked_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="likes", lazy="select")
    song = relationship("Song", back_populates="likes", lazy="select")

    __table_args__ = (
        UniqueConstraint("user_id", "song_id", name="uq_user_song_like"),
        Index("idx_likes_user_song", "user_id", "song_id"),
    )

    def __repr__(self):
        return f"<Like id={self.id} user_id={self.user_id} song_id={self.song_id} liked_at={self.liked_at}>"
