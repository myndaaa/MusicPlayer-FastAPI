from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Album(Base):
    __tablename__ = "album"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String(255), nullable=True)
    release_date = Column(DateTime, nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Nullable artist or band 
    album_artist_id = Column(Integer, ForeignKey("artist.id", ondelete="SET NULL"), nullable=True)
    album_band_id = Column(Integer, ForeignKey("band.id", ondelete="SET NULL"), nullable=True)
    artist_name_text = Column(String(100), nullable=True)
    band_name_text = Column(String(100), nullable=True)


    # Relationships
    artist = relationship("Artist", back_populates="albums", lazy="select")
    band = relationship("Band", back_populates="albums", lazy="select")
    album_songs = relationship("AlbumSongs", back_populates="album", cascade="all, delete-orphan", lazy="select")
    uploaded_by = relationship("User", back_populates="uploaded_albums", lazy="select")

    def __repr__(self):
        return f"<Album id={self.id} title='{self.title}' release_date={self.release_date}>"
