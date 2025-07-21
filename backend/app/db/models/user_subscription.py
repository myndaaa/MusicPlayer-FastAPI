from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserSubscription(Base):
    __tablename__ = "user_subscription"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plan.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_auto_renew = Column(Boolean, default=True, nullable=False)
    is_cancelled = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions", lazy="select")
    plan = relationship("SubscriptionPlan", back_populates="user_subscriptions", lazy="select")

    def __repr__(self):
        return f"<UserSubscription id={self.id} user_id={self.user_id} plan_id={self.plan_id}>"
