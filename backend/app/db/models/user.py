# app/db/models/user.py

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum, Index, UniqueConstraint 
from app.db.base_class import Base
from sqlalchemy.orm import relationship


''' -> commented out code to be removed later after schema creation
# Roles using Python Enum 
class UserRole(str, enum.Enum):
    superadmin = "admin"
    singer = "artist"
    listener = "listener"
'''

class User(Base):
    __tablename__ = "users"  

    # Primary Key
    id = Column(Integer, primary_key=True)  

    # User Info
    username = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)


    # Audit Fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    disabled_at = Column(DateTime, nullable=True)
    

    # Relationships

    # system_config entries updated by this user 
    system_configs = relationship("SystemConfig", back_populates="updated_by_admin", lazy="select")
    # localization entries updated by this user
    localizations = relationship("Localization", back_populates="updated_by_user", lazy="select")
    # audit logs created by this user
    audit_logs = relationship("AuditLog", back_populates="user", lazy="select")
    # History entries
    history = relationship("History", back_populates="user", lazy="select", cascade="all, delete-orphan")
    # Likes given by the user
    likes = relationship("Likes", back_populates="user", lazy="select", cascade="all, delete-orphan")
    # Playlists owned by the user
    playlists = relationship("Playlist", back_populates="owner", lazy="select")
    # Playlist Collaborations where user is collaborator
    playlist_collaborations = relationship("PlaylistCollaborator", back_populates="collaborator", lazy="select", foreign_keys="PlaylistCollaborator.collaborator_user_id")
    # Playlist Collaborations where user invited others
    added_collaborators = relationship("PlaylistCollaborator", back_populates="added_by", lazy="select", foreign_keys="PlaylistCollaborator.added_by_user_id")
    # Following (users followed by this user)
    following = relationship("Following", back_populates="follower", lazy="select", foreign_keys="Following.following_user_id")
    # UserSubscriptions
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # Payments made by the user
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan", lazy="select")
    # Artist profile linked to this user
    artist_profile = relationship("Artist", back_populates="linked_user", uselist=False, lazy="select")
    # Artist or bands this user is following
    followings = relationship("Following", back_populates="user", lazy="select", cascade="all, delete-orphan")
    # Admin uploads songs
    uploaded_songs = relationship("Song", back_populates="uploaded_by", lazy="select")
    # Admin uploads albums
    uploaded_albums = relationship("Album", back_populates="uploaded_by", lazy="select")

    
    # Table-level constraints
    __table_args__ = (
    UniqueConstraint("username", name="uq_user_username"),
    UniqueConstraint("email", name="uq_user_email"),  
    Index("idx_user_username", "username"),
    Index("idx_user_email", "email"),  
)

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"