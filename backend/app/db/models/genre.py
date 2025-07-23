
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True)
    disabled_at = Column(DateTime, nullable=True)


    # Relationship
    songs = relationship("Song", back_populates="genre", lazy="select")

    __table_args__ = (
        UniqueConstraint("name", name="uq_genre_name"),
        Index("idx_genre_name", "name"),
    )

    def __repr__(self):
        return f"<Genre id={self.id} name='{self.name}'>"

