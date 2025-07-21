# app/db/models/localization.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone


class Localization(Base):
    __tablename__ = "localization"

    id = Column(Integer, primary_key=True, autoincrement=True)

    translation_key = Column(String(100), nullable=False)
    language_code = Column(String(10), nullable=False)
    translation_value = Column(Text, nullable=False)

    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    updated_by_user_id = Column(
        Integer,
        ForeignKey("user.id", name="fk_localization_updated_by_user__user"),
        nullable=False,
    )

    # Relationships
    updated_by_user = relationship("User", lazy="select")

    __table_args__ = (
        Index("ix_localization_translation_key", "translation_key"),
    )

    def __repr__(self):
        return (
            f"<Localization id={self.id} lang={self.language_code} "
            f"key='{self.translation_key}' updated_by={self.updated_by_user_id}>"
        )
