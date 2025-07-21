
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # who did it
    user_id = Column(Integer,ForeignKey("user.id", name="fk_audit_log_user__user"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_table = Column(String(50), nullable=False)
    target_id = Column(Integer, nullable=True)  
    action_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


    # Relationships
    user = relationship("User", back_populates="audit_logs", lazy="select")
    

    __table_args__ = (
        Index("ix_audit_log_target_table", "target_table"),
        Index("ix_audit_log_action_type", "action_type"),
    )

    def __repr__(self):
        return (
            f"<AuditLog id={self.id} user_id={self.user_id} action={self.action_type} "
            f"target={self.target_table}:{self.target_id}>"
        )
