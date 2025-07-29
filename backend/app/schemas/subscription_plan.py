from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Annotated
from pydantic import StringConstraints, condecimal, conint


class SubscriptionPlanBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    price: Annotated[float, condecimal(gt=0, max_digits=10, decimal_places=2)]  # > 0 price
    duration_days: Annotated[int, conint(gt=0)]  # must be positive integer
    description: Optional[str] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass  # created_at and is_active handled in CRUD


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = None
    price: Optional[Annotated[float, condecimal(gt=0, max_digits=10, decimal_places=2)]] = None
    duration_days: Optional[Annotated[int, conint(gt=0)]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionPlanOut(SubscriptionPlanBase):
    id: int
    is_active: bool
    offer_created_at: datetime

    class Config:
        orm_mode = True
