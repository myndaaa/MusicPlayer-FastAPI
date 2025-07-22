from sqlalchemy import Column, Integer, ForeignKey, Index
from app.db.base_class import Base
from sqlalchemy.orm import relationship


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    playlist_song_id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id", ondelete="CASCADE"), nullable=False)
    song_order = Column(Integer, nullable=True)

    # Relationships
    playlist = relationship("Playlist", back_populates="playlist_songs", lazy="select")
    song = relationship("Song", back_populates="playlist_songs", lazy="select")

    __table_args__ = (
        Index("ix_playlist_song", "playlist_id", "song_id"),
    )

    def __repr__(self):
        return f"<PlaylistSongs id={self.playlist_song_id} playlist_id={self.playlist_id} song_id={self.song_id}>"
