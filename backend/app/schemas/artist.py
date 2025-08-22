from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, StringConstraints, field_validator
from typing_extensions import Annotated

ShortStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
LongStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
UrlStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]

class ArtistBase(BaseModel):
    artist_stage_name: ShortStr
    artist_bio: Optional[LongStr] = None
    artist_profile_image: Optional[UrlStr] = None
    artist_social_link: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ArtistCreate(ArtistBase):
    pass

class ArtistUpdate(BaseModel):
    artist_stage_name: Optional[ShortStr] = None
    artist_bio: Optional[LongStr] = None
    artist_profile_image: Optional[UrlStr] = None
    artist_social_link: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ArtistOut(ArtistBase):
    id: int
    linked_user_account: int
    created_at: datetime
    is_disabled: bool
    disabled_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ArtistSignup(BaseModel):
    username: ShortStr
    first_name: ShortStr
    last_name: ShortStr
    email: str
    password: str
    
    artist_stage_name: ShortStr
    artist_bio: Optional[LongStr] = None
    artist_profile_image: Optional[UrlStr] = None
    artist_social_link: Optional[Dict[str, Any]] = None

    @field_validator("artist_stage_name")
    @classmethod
    def validate_stage_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Stage name cannot be empty")
        if len(value.strip()) < 2:
            raise ValueError("Stage name must be at least 2 characters long")
        return value.strip()

class ArtistProfileUpdate(ArtistUpdate):
    pass

class ArtistAdminUpdate(ArtistUpdate):
    is_disabled: Optional[bool] = None


class ArtistSignupUserInfo(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class ArtistSignupArtistInfo(BaseModel):
    id: int
    stage_name: str
    bio: Optional[str] = None

    class Config:
        from_attributes = True


class ArtistSignupResponse(BaseModel):
    message: str
    user: ArtistSignupUserInfo
    artist: ArtistSignupArtistInfo

    class Config:
        from_attributes = True

