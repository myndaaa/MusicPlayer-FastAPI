# app/db/models/user.py

import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, Index, UniqueConstraint 
from app.db.base import Base


# Roles using Python Enum 
class UserRole(str, enum.Enum):
    superadmin = "admin"
    singer = "artist"
    listener = "listener"


class User(Base):
    __tablename__ = "user"  

    # Primary Key
    id = Column(Integer, primary_key=True)  

    # User Info
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)  # Enum for role handling

    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    disabled_at = Column(DateTime, nullable=True)
    
    
    # Table-level constraints
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),  # constraint
        Index("ix_user_username", "username"),  # Index 
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"