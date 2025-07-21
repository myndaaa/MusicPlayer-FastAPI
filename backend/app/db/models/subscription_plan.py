from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    duration_days = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    offer_created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="plan", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
        return f"<SubscriptionPlan id={self.id} name={self.name} active={self.is_active}>"
