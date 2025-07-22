from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Playlist(Base):
    __tablename__ = "playlists"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Foreign Key to User 
    owner_id = Column(Integer,ForeignKey("users.id", name="fk_playlist_owner_id_users"), nullable=False,)

    # Playlist details
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="playlists", lazy="select")
    playlist_songs = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan", lazy="select")
    playlist_collaborators = relationship("PlaylistCollaborator", back_populates="playlist", cascade="all, delete-orphan", lazy="select")

    # Indexes and Constraints
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_playlist_owner_name"),  # optional uniqueness for user playlists
        Index("ix_playlist_owner_id", "owner_id"),
    )

    def __repr__(self):
        return f"<Playlist id={self.playlist_id} name={self.name} owner_id={self.owner_id}>"
