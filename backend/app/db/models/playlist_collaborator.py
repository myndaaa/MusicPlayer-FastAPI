from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class PlaylistCollaborator(Base):
    __tablename__ = "playlist_collaborator"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey("playlist.id", ondelete="CASCADE"), nullable=False)
    collaborator_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    added_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    added_by_user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_collaborators", lazy="select")
    collaborator = relationship("User", foreign_keys=[collaborator_id], back_populates="playlist_collaborations", lazy="select")
    added_by = relationship("User", foreign_keys=[added_by_user_id], back_populates="added_collaborators", lazy="select")

    __table_args__ = (
        Index("ix_playlist_collaborator", "playlist_id", "collaborator_id"),
    )

    def __repr__(self):
        return f"<PlaylistCollaborator id={self.playlist_collaborator_id} playlist_id={self.playlist_id} collaborator_id={self.collaborator_id}>"
