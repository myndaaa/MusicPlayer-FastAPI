from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Enum, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"


class PaymentMethodEnum(str, enum.Enum):
    paypal = "paypal"   
    credit_card = "credit_card"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    transaction_reference = Column(String(255), nullable=False, unique=True)
    payment_created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    payment_completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments", lazy="select")

    def __repr__(self):
        return f"<Payment id={self.id} user_id={self.user_id} status={self.payment_status}>"
    