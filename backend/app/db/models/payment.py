from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.db.base import Base

''' --> commented out code to be removed later after schema creation
class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class PaymentMethodEnum(str, enum.Enum):
    paypal = "paypal"   
    credit_card = "credit_card"
'''

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(100), nullable=False)
    method = Column(String(100), nullable=False)
    transaction_reference = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments", lazy="select")

    # Indexes
    __table_args__ = (
        Index("idx_payments_user_id", "user_id"),
        Index("idx_payments_status", "payment_status"),
        Index("idx_payments_created_at", "payment_created_at"),
        Index("idx_payments_method", "payment_method"),
    )


    def __repr__(self):
        return f"<Payment id={self.id} user_id={self.user_id} status={self.payment_status}>"
    