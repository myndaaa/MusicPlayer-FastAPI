from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy import Index

class AlbumSong(Base):
    __tablename__ = "album_songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    track_number = Column(Integer, nullable=False)

    # Relationships
    album = relationship("Album", back_populates="album_songs", lazy="select")
    song = relationship("Song", back_populates="album_songs", lazy="select")

    __table_args__ = (
        UniqueConstraint("album_id", "track_number", name="uq_album_track"),
    )
    __table_args__ = (
        UniqueConstraint("album_id", "track_number", name="uq_album_track"),
        Index("idx_album_song_album_id", "album_id"),
    )



    def __repr__(self):
        return f"<AlbumSongs id={self.id} album_id={self.album_id} song_id={self.song_id} track={self.track_number}>"
