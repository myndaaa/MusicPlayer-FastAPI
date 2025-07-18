# app/db/models/song.py

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Song(Base):
    __tablename__ = "song"  

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Song details
    title = Column(String(150), nullable=False)
    genre_id = Column(Integer, ForeignKey("genre.id"), nullable=False)
    band_id = Column(Integer, ForeignKey("band.band_id"), nullable=True)
    artist_id = Column(Integer, ForeignKey("artist.id"), nullable=True)
    release_date = Column(DateTime, nullable=False)
    song_duration = Column(Integer, nullable=False)  # Duration in seconds
    file_path = Column(String(255), nullable=False)
    cover_image = Column(String(255), nullable=True)

    # Relationships
    genre = relationship("Genre", lazy="select")
    band = relationship("Band", lazy="select")
    artist = relationship("Artist", lazy="select")

    # Audit and Soft Delete
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_disabled = Column(Boolean, default=False, nullable=False)
    disabled_at = Column(DateTime, nullable=True)

    # Indexes
    __table_args__ = (
        Index("ix_song_title", "title"),
        Index("ix_song_genre_id", "genre_id"),
        Index("ix_song_artist_id", "artist_id"),
        Index("ix_song_band_id", "band_id"),
    )

    def __repr__(self):
        return (
            f"<Song id={self.id} title='{self.title}' "
            f"artist_id={self.artist_id} band_id={self.band_id} disabled={self.is_disabled}>"
        )
