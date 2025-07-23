from datetime import datetime
from sqlalchemy import Column, Index, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String(255), nullable=True)
    release_date = Column(DateTime, nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Nullable artist or band 
    album_artist_id = Column(Integer, ForeignKey("artists.id", ondelete="SET NULL"), nullable=True)
    album_band_id = Column(Integer, ForeignKey("bands.id", ondelete="SET NULL"), nullable=True)
    artist_name = Column(String(100), nullable=True)
    band_name = Column(String(100), nullable=True)


    # Relationships
    artist = relationship("Artist", back_populates="albums", lazy="select")
    band = relationship("Band", back_populates="albums", lazy="select")
    album_songs = relationship("AlbumSong", back_populates="album", cascade="all, delete-orphan", lazy="select")
    uploaded_by = relationship("User", back_populates="uploaded_albums", lazy="select")

    __table_args__ = (
        Index("idx_album_artist_id", "album_artist_id"),
        Index("idx_album_band_id", "album_band_id"),
        Index("idx_album_title", "title"),
    )

    def __repr__(self):
        return f"<Album id={self.id} title='{self.title}' artist_id={self.album_artist_id} band_id={self.album_band_id}>"

