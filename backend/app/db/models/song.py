# app/db/models/song.py

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Song(Base):
    __tablename__ = "songs"  

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Song details
    title = Column(String(150), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    band_id = Column(Integer, ForeignKey("bands.id"), nullable=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=True)
    release_date = Column(DateTime, nullable=False)
    song_duration = Column(Integer, nullable=False)  # Duration in seconds
    file_path = Column(String(255), nullable=False)
    cover_image = Column(String(255), nullable=True)
    artist_name_text = Column(String(100), nullable=True)
    band_name_text = Column(String(100), nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


    # Relationships
   
    genre = relationship("Genre", back_populates="songs", lazy="select")
    band = relationship("Band", back_populates="songs", lazy="select")
    artist = relationship("Artist", back_populates="songs", lazy="select")
    histories = relationship("History", back_populates="song", lazy="select", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="song", lazy="select", cascade="all, delete-orphan")
    playlist_songs = relationship("PlaylistSong", back_populates="song", lazy="select")
    album_songs = relationship("AlbumSong", back_populates="song", lazy="select", cascade="all, delete-orphan")
    uploaded_by = relationship("User", back_populates="uploaded_songs", lazy="select")


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
