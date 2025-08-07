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

# Password validation function for reusability
def validate_password_strength(value: str) -> str:
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

# Core UserBase - most reusable, contains only essential user fields
class UserBase(BaseModel):
    username: ShortStr
    first_name: ShortStr
    last_name: ShortStr
    email: EmailStr

    class Config:
        from_attributes = True

# UserBase with role - for cases where role is needed
class UserBaseWithRole(UserBase):
    role: UserRole

    class Config:
        from_attributes = True
        use_enum_values = True  # Ensures role = "admin", not UserRole.admin

# UserBase with password - for signup/creation
class UserBaseWithPassword(UserBase):
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password_strength(value)

# UserBase with role and password - for admin creation
class UserBaseWithRoleAndPassword(UserBaseWithRole):
    password: PasswordStr

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password_strength(value)

# Signup schema - no role specified (defaults to listener)
class UserSignup(UserBaseWithPassword):
    pass

# Create schema - includes role (for admin use)
class UserCreate(UserBaseWithRoleAndPassword):
    pass

# Update schema - all fields optional, inherits from UserBase
class UserUpdate(UserBase):
    username: Optional[ShortStr] = None
    first_name: Optional[ShortStr] = None
    last_name: Optional[ShortStr] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True

# Password update schema
class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: PasswordStr

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return validate_password_strength(value)

# Login schema
class UserLogin(BaseModel):
    username: str
    password: str

# Output schema - includes all user fields plus system fields
class UserOut(UserBaseWithRole):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True  # Ensures JSON contains string values for enums

# Database schema - includes hashed password
class UserInDB(UserOut):
    password: str  # hashed

# Status schema - for user status information
class UserStatus(BaseModel):
    is_active: bool
    disabled_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
