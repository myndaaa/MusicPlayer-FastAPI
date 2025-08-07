from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.db.models.artist import Artist
from app.db.models.user import User
from app.schemas.artist import ArtistCreate, ArtistUpdate, ArtistSignup, ArtistStats
from app.core.security import hash_password


def create_artist(db: Session, artist_data: ArtistCreate, user_id: int) -> Artist:
    """
    Create a new artist profile linked to an existing user.
    Args:
        db: Database session
        artist_data: Artist creation data
        user_id: ID of the user to link the artist profile to
    Returns:
        Created artist object
    Raises:
        ValueError: If user doesn't exist or is already an artist
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    if is_user_already_an_artist(db, user_id):
        raise ValueError("User is already an artist")
    
    artist = Artist(
        artist_stage_name=artist_data.artist_stage_name,
        artist_bio=artist_data.artist_bio,
        artist_profile_image=artist_data.artist_profile_image,
        artist_social_link=artist_data.artist_social_link,
        linked_user_account=user_id,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(artist)
    db.flush()
    db.refresh(artist)
    return artist


def create_artist_with_user(db: Session, artist_signup_data: ArtistSignup) -> Tuple[User, Artist]:
    """
    Create both user (with musician role) and artist profile in one transaction.
    Args:
        db: Database session
        artist_signup_data: Combined user and artist signup data
    Returns:
        Tuple of (created_user, created_artist)
    Raises:
        ValueError: If username, email, or stage name already exists
    """
    existing_user = db.query(User).filter(
        or_(User.username == artist_signup_data.username, User.email == artist_signup_data.email)
    ).first()
    if existing_user:
        raise ValueError("Username or email already exists")
    
    if stage_name_taken(db, artist_signup_data.artist_stage_name):
        raise ValueError("Stage name already taken")
    
    user = User(
        username=artist_signup_data.username,
        first_name=artist_signup_data.first_name,
        last_name=artist_signup_data.last_name,
        email=artist_signup_data.email,
        password=hash_password(artist_signup_data.password),
        role="musician",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(user)
    db.flush()
    db.refresh(user)
    

    artist = create_artist(db, ArtistCreate(
        artist_stage_name=artist_signup_data.artist_stage_name,
        artist_bio=artist_signup_data.artist_bio,
        artist_profile_image=artist_signup_data.artist_profile_image,
        artist_social_link=artist_signup_data.artist_social_link
    ), user.id)
    
    return user, artist


def get_artist_by_id(db: Session, artist_id: int) -> Optional[Artist]:
    """
    Get artist by primary key.
    Args:
        db: Database session
        artist_id: Artist ID to retrieve
    Returns:
        Artist object if found, None otherwise
    """
    return db.query(Artist).filter(Artist.id == artist_id).first()


def get_artist_by_user_id(db: Session, user_id: int) -> Optional[Artist]:
    """
    Get artist profile for a specific user.
    Args:
        db: Database session
        user_id: User ID to find artist profile for
    Returns:
        Artist object if found, None otherwise
    """
    return db.query(Artist).filter(Artist.linked_user_account == user_id).first()


def get_artist_by_stage_name(db: Session, stage_name: str) -> Optional[Artist]:
    """
    Get artist by their stage name.
    Args:
        db: Database session
        stage_name: Stage name to search for
    Returns:
        Artist object if found, None otherwise
    """
    return db.query(Artist).filter(Artist.artist_stage_name == stage_name).first()


def get_all_artists(db: Session, skip: int = 0, limit: int = 10) -> List[Artist]:
    """
    Get paginated list of all artists.
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
    Returns:
        List of artist objects
    """
    return db.query(Artist).offset(skip).limit(limit).all()


def get_all_active_artists(db: Session, skip: int = 0, limit: int = 10) -> List[Artist]:
    """
    Get only active (non-disabled) artists.
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of active artist objects
    """
    return db.query(Artist).filter(Artist.is_disabled == False).offset(skip).limit(limit).all()


def search_artists_by_name(db: Session, keyword: str, skip: int = 0, limit: int = 10) -> List[Artist]:
    """
    Case-insensitive search by stage name.
    Args:
        db: Database session
        keyword: Search keyword
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of matching artist objects
    """
    return db.query(Artist).filter(
        Artist.artist_stage_name.ilike(f"%{keyword}%")
    ).offset(skip).limit(limit).all()


def update_artist(db: Session, artist_id: int, data: ArtistUpdate) -> Optional[Artist]:
    """
    Update artist profile (stage name, bio, image, social links).    
    Args:
        db: Database session
        artist_id: Artist ID to update
        data: Update data
    Returns:
        Updated artist object if found, None otherwise
    Raises:
        ValueError: If stage name is already taken by another artist
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return None
    if data.artist_stage_name and data.artist_stage_name != artist.artist_stage_name:
        if stage_name_taken(db, data.artist_stage_name, exclude_artist_id=artist_id):
            raise ValueError("Stage name already taken")
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(artist, field, value)
    
    db.add(artist)
    db.flush()
    db.refresh(artist)
    return artist


def update_artist_by_user_id(db: Session, user_id: int, data: ArtistUpdate) -> Optional[Artist]:
    """
    Update artist profile using user ID.
    Args:
        db: Database session
        user_id: User ID to find artist profile
        data: Update data
    Returns:
        Updated artist object if found, None otherwise
    """
    artist = get_artist_by_user_id(db, user_id)
    if not artist:
        return None
    return update_artist(db, artist.id, data)

def disable_artist(db: Session, artist_id: int) -> bool:
    """
    Disable an artist account.    
    Args:
        db: Database session
        artist_id: Artist ID to disable
    Returns:
        True if artist was disabled, False if not found
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return False
    
    artist.is_disabled = True
    artist.disabled_at = datetime.now(timezone.utc)
    db.add(artist)
    db.flush()
    db.refresh(artist)
    return True


def enable_artist(db: Session, artist_id: int) -> bool:
    """
    Enable a disabled artist account.
    Args:
        db: Database session
        artist_id: Artist ID to enable
    Returns:
        True if artist was enabled, False if not found
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return False
    
    artist.is_disabled = False
    artist.disabled_at = None
    db.add(artist)
    db.flush()
    db.refresh(artist)
    return True


def disable_artist_by_user_id(db: Session, user_id: int) -> bool:
    """
    Disable artist using user ID.
    Args:
        db: Database session
        user_id: User ID to find and disable artist profile
    Returns:
        True if artist was disabled, False if not found
    """
    artist = get_artist_by_user_id(db, user_id)
    if not artist:
        return False
    return disable_artist(db, artist.id)


def enable_artist_by_user_id(db: Session, user_id: int) -> bool:
    """
    Enable artist using user ID.
    Args:
        db: Database session
        user_id: User ID to find and enable artist profile
        
    Returns:
        True if artist was enabled, False if not found
    """
    artist = get_artist_by_user_id(db, user_id)
    if not artist:
        return False
    return enable_artist(db, artist.id)


def delete_artist(db: Session, artist_id: int) -> bool:
    """
    Delete artist (only if cascade-safe).
    Args:
        db: Database session
        artist_id: Artist ID to delete
    Returns:
        True if artist was deleted, False if not found or not safe to delete
    """
    artist = get_artist_by_id(db, artist_id)
    if not artist:
        return False
    if artist.songs or artist.albums:
        return False  # Not safe to delete
    
    db.delete(artist)
    db.flush()
    return True

def artist_exists(db: Session, artist_id: int) -> bool:
    """
    Check if artist exists.
    Args:
        db: Database session
        artist_id: Artist ID to check
    Returns:
        True if artist exists, False otherwise
    """
    return db.query(Artist).filter(Artist.id == artist_id).first() is not None


def is_user_already_an_artist(db: Session, user_id: int) -> bool:
    """
    Check if user already has artist profile.
    Args:
        db: Database session
        user_id: User ID to check
    Returns:
        True if user is already an artist, False otherwise
    """
    return get_artist_by_user_id(db, user_id) is not None


def stage_name_taken(db: Session, stage_name: str, exclude_artist_id: Optional[int] = None) -> bool:
    """
    Check if stage name is already taken.
    Args:
        db: Database session
        stage_name: Stage name to check
        exclude_artist_id: Artist ID to exclude from check (for updates)
    Returns:
        True if stage name is taken, False otherwise
    """
    query = db.query(Artist).filter(Artist.artist_stage_name == stage_name)
    
    if exclude_artist_id:
        query = query.filter(Artist.id != exclude_artist_id)
    return query.first() is not None


def get_artist_count(db: Session) -> int:
    """
    Get total number of artists.
    Args:
        db: Database session
    Returns:
        Total count of artists
    """
    return db.query(func.count(Artist.id)).scalar()


def get_active_artist_count(db: Session) -> int:
    """
    Get count of active artists.
    Args:
        db: Database session
    Returns:
        Count of active artists
    """
    return db.query(func.count(Artist.id)).filter(Artist.is_disabled == False).scalar()


def get_artist_with_related_entities(db: Session, artist_id: int) -> Optional[Artist]:
    """
    Get artist with eager-loaded relationships (songs, albums, followers).
    Args:
        db: Database session
        artist_id: Artist ID to retrieve
    Returns:
        Artist object with loaded relationships if found, None otherwise
    """
    return db.query(Artist).options(
        db.joinedload(Artist.songs),
        db.joinedload(Artist.albums),
        db.joinedload(Artist.followers)
    ).filter(Artist.id == artist_id).first()


def get_artists_followed_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Artist]:
    """
    Get artists that a specific user follows.
    Args:
        db: Database session
        user_id: User ID to get followed artists for
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of artists that the user follows
    """
    return db.query(Artist).join(Artist.followers).filter(
        Artist.followers.any(user_id=user_id)
    ).offset(skip).limit(limit).all()


def get_artist_statistics(db: Session) -> ArtistStats:
    """
    Get comprehensive artist statistics for admin dashboard.
    Args:
        db: Database session
    Returns:
        ArtistStats object with various counts
    """
    total_artists = get_artist_count(db)
    active_artists = get_active_artist_count(db)
    disabled_artists = total_artists - active_artists
    
    artists_with_songs = db.query(func.count(func.distinct(Artist.id))).join(
        Artist.songs
    ).scalar()
    artists_with_albums = db.query(func.count(func.distinct(Artist.id))).join(
        Artist.albums
    ).scalar()
    
    return ArtistStats(
        total_artists=total_artists,
        active_artists=active_artists,
        disabled_artists=disabled_artists,
        artists_with_songs=artists_with_songs or 0,
        artists_with_albums=artists_with_albums or 0
    )
