
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime,  timezone


class SystemConfig(Base):
    __tablename__ = "system_configs"

    # descriptive key for config settings
    config_key = Column(String(100), primary_key=True)
    config_value = Column(String(100), nullable=False)  # value of config as string
    config_description = Column(Text, nullable=True)
    config_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)# last update time
    config_updated_by_admin_id = Column(ForeignKey("users.id", name="fk_system_config_updated_by_admin__user"),nullable=False)  # user who updated this config

    # Relationships'
    updated_by_admin = relationship("User", back_populates="system_configs", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index("idx_system_config_config_key", "config_key"),
    )

    def __repr__(self):
        return (
            f"<SystemConfig key={self.config_key} value={self.config_value} "
            f"updated_by={self.config_updated_by_admin_id}>"
        )
