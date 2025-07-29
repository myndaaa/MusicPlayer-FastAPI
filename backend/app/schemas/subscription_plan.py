from typing import Optional, Annotated
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, StringConstraints, Field


class SubscriptionPlanBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    duration_days: Annotated[int, Field(gt=0)]
    description: Optional[str] = None

    class Config:
        from_attributes = True  


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass  # TODO: created_at and is_active handled in CRUD


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = None
    price: Optional[Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]] = None
    duration_days: Optional[Annotated[int, Field(gt=0)]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class SubscriptionPlanOut(SubscriptionPlanBase):
    id: int
    is_active: bool
    offer_created_at: datetime

    class Config:
        from_attributes = True  
