from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints


class SystemConfigBase(BaseModel):
    config_key: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    config_value: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    config_description: Optional[str] = None

    class Config:
        from_attributes = True

class SystemConfigCreate(SystemConfigBase):
    pass  # no additional fields needed on create


class SystemConfigUpdate(BaseModel):
    config_value: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    config_description: Optional[str] = None

    class Config:
        from_attributes = True



class SystemConfigOut(SystemConfigBase):
    config_updated_at: datetime
    config_updated_by_admin_id: int

    class Config:
        from_attributes = True 

class AdminUserMinimal(BaseModel):
    id: int
    username: str 

    class Config:
        from_attributes = True


class SystemConfigWithAdminOut(SystemConfigOut):
    updated_by_admin: AdminUserMinimal

    class Config:
        from_attributes = True
