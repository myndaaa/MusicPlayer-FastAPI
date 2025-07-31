from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, EmailStr, StringConstraints, field_validator
import re
import enum

# Enums for User Roles

class UserRole(str, enum.Enum):
    admin = "admin"
    listener = "listener"
    musician = "musician"

# String Constraints for User Input
ShortStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
PasswordStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=255)]


class UserBase(BaseModel):
    username: ShortStr
    first_name: ShortStr
    last_name: ShortStr
    email: EmailStr
    role: UserRole  # accepted in input, saved to DB as string

    class Config:
        from_attributes = True
        use_enum_values = True  # Ensures role = "admin", not UserRole.admin


class UserCreate(UserBase):
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        """
        Enforces strong password: One uppercase, one lowercase, one special char
        """
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not re.search(r"[\W_]", value):
            raise ValueError("Password must include at least one special character.")
        return value


class UserUpdate(BaseModel):
    username: Optional[ShortStr]
    first_name: Optional[ShortStr]
    last_name: Optional[ShortStr]
    email: Optional[EmailStr]

    class Config:
        from_attributes = True


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: PasswordStr

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not re.search(r"[\W_]", value):
            raise ValueError("Password must include at least one special character.")
        return value


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True  # Ensures JSON contains string values for enums

class UserInDB(UserOut):
    password: str  # hashed


class UserStatus(BaseModel):
    is_active: bool
    disabled_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
