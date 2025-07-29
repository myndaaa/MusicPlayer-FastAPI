from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from typing import Annotated
from pydantic import StringConstraints


class LocalizationBase(BaseModel):
    translation_key: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    language_code: Annotated[str, StringConstraints(strip_whitespace=True, max_length=10)]
    translation_value: str


class LocalizationCreate(LocalizationBase):
    pass  # Same fields, updated_by_user_id set in CRUD


class LocalizationUpdate(BaseModel):
    translation_value: str


class LocalizationOut(LocalizationBase):
    id: int
    updated_at: datetime
    updated_by_user_id: int # ID of the user who last updated this localization

    class Config:
        orm_mode = True



class UserBasicInfo(BaseModel):
    id: int
    email: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


class LocalizationWithUser(LocalizationOut):
    updated_by_user: Optional[UserBasicInfo] = None
