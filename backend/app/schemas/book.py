from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, StringConstraints


# Shared base schema for band
class BandBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
    bio: Optional[str] = None
    profile_picture: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    social_link: Optional[dict] = None  # dict 


# Schema for band creation
class BandCreate(BandBase):
    pass  # inherits everything


# Schema for band update (all fields optional)
class BandUpdate(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]] = None
    bio: Optional[str] = None
    profile_picture: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    social_link: Optional[dict] = None


# Output schema for read operations
class BandOut(BandBase):
    id: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        orm_mode = True


