from typing import Optional
from datetime import datetime
from typing_extensions import Annotated
from pydantic import BaseModel, constr


class SystemConfigBase(BaseModel):
    config_key: Annotated[str, constr(strip_whitespace=True, max_length=100)]
    config_value: Annotated[str, constr(strip_whitespace=True, max_length=100)]
    config_description: Optional[str] = None

class SystemConfigCreate(SystemConfigBase):
    pass  # no additional fields needed on create


class SystemConfigUpdate(BaseModel):
    config_value: Annotated[str, constr(strip_whitespace=True, max_length=100)]
    config_description: Optional[str] = None



class SystemConfigOut(SystemConfigBase):
    config_updated_at: datetime
    config_updated_by_admin_id: int

    class Config:
        orm_mode = True  # enables reading data from ORM model

class AdminUserMinimal(BaseModel):
    id: int
    username: str 

    class Config:
        orm_mode = True


class SystemConfigWithAdminOut(SystemConfigOut):
    updated_by_admin: AdminUserMinimal

    class Config:
        orm_mode = True
