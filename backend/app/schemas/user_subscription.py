from typing import Optional, List, Annotated
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator


# Base schema for user subscription
class UserSubscriptionBase(BaseModel):
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_auto_renew: bool = True
    is_cancelled: bool = False

    @model_validator(mode="after")
    def validate_dates(self) -> "UserSubscriptionBase":
        """Ensure end_date is after start_date"""
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

    class Config:
        from_attributes = True


class UserSubscriptionCreate(UserSubscriptionBase):
    pass


class UserSubscriptionUpdate(BaseModel):
    end_date: Optional[datetime] = None
    is_auto_renew: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSubscriptionOut(UserSubscriptionBase):
    id: int
    cancelled_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas for relationships
class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


class SubscriptionPlanMinimal(BaseModel):
    id: int
    name: str
    price: Decimal
    duration_days: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


# User subscription output with relationships
class UserSubscriptionWithRelations(UserSubscriptionOut):
    user: UserMinimal
    plan: SubscriptionPlanMinimal


# User subscription with status
class UserSubscriptionWithStatus(UserSubscriptionWithRelations):
    is_active: bool
    days_remaining: int
    is_expired: bool
    can_renew: bool


# List schemas for pagination
class UserSubscriptionList(BaseModel):
    subscriptions: List[UserSubscriptionOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserSubscriptionListWithRelations(BaseModel):
    subscriptions: List[UserSubscriptionWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class UserSubscriptionFilter(BaseModel):
    user_id: Optional[int] = None
    plan_id: Optional[int] = None
    is_auto_renew: Optional[bool] = None
    is_cancelled: Optional[bool] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    end_date_from: Optional[datetime] = None
    end_date_to: Optional[datetime] = None


# Subscription management schemas
class UserSubscriptionRenew(BaseModel):
    subscription_id: int
    extend_days: Optional[int] = None  # if none use plans duration_days


class UserSubscriptionCancel(BaseModel):
    subscription_id: int
    cancel_at_end: bool = True  # If false -> cancel 


class UserSubscriptionUpgrade(BaseModel):
    current_subscription_id: int
    new_plan_id: int
    prorate: bool = True  # Whether to prorate the remaining time


# Subscription statistics
class UserSubscriptionStats(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    cancelled_subscriptions: int
    total_revenue: Decimal
    average_subscription_duration: int  # in days


# User subscription history
class UserSubscriptionHistory(BaseModel):
    user_id: int
    subscriptions: List[UserSubscriptionWithRelations]
    total_spent: Decimal
    current_plan: Optional[SubscriptionPlanMinimal] = None
    subscription_history: List[UserSubscriptionOut] = [] 
