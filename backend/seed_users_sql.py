#!/usr/bin/env python3
"""
SQL-based User Seeding Script for Music Player API

This script creates test users (admin, musician, listener) for development and testing.
Users are created with credentials from the .env file using raw SQL to avoid model issues.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
from app.core.security import hash_password


def load_env_vars():
    """Load environment variables from settings with fallbacks"""
    # Check if test credentials are configured
    if not settings.TEST_ADMIN_USERNAME:
        print("Test credentials not found in .env file")
        print("Please add test credentials to your .env file:")
        print("""
# Test User Credentials
TEST_ADMIN_USERNAME=test_admin
TEST_ADMIN_EMAIL=admin@test.com
TEST_ADMIN_PASSWORD=AdminPass123!
TEST_ADMIN_FIRST_NAME=Test
TEST_ADMIN_LAST_NAME=Admin

TEST_MUSICIAN_USERNAME=test_musician
TEST_MUSICIAN_EMAIL=musician@test.com
TEST_MUSICIAN_PASSWORD=MusicianPass123!
TEST_MUSICIAN_FIRST_NAME=Test
TEST_MUSICIAN_LAST_NAME=Musician
TEST_MUSICIAN_STAGE_NAME=Test Musician
TEST_MUSICIAN_BIO=A test musician for development

TEST_LISTENER_USERNAME=test_listener
TEST_LISTENER_EMAIL=listener@test.com
TEST_LISTENER_PASSWORD=ListenerPass123!
TEST_LISTENER_FIRST_NAME=Test
TEST_LISTENER_LAST_NAME=Listener
        """)
        return None
    
    return {
        'admin': {
            'username': settings.TEST_ADMIN_USERNAME,
            'email': settings.TEST_ADMIN_EMAIL,
            'password': settings.TEST_ADMIN_PASSWORD,
            'first_name': settings.TEST_ADMIN_FIRST_NAME,
            'last_name': settings.TEST_ADMIN_LAST_NAME,
            'role': 'admin'
        },
        'musician': {
            'username': settings.TEST_MUSICIAN_USERNAME,
            'email': settings.TEST_MUSICIAN_EMAIL,
            'password': settings.TEST_MUSICIAN_PASSWORD,
            'first_name': settings.TEST_MUSICIAN_FIRST_NAME,
            'last_name': settings.TEST_MUSICIAN_LAST_NAME,
            'role': 'musician',
            'stage_name': settings.TEST_MUSICIAN_STAGE_NAME,
            'bio': settings.TEST_MUSICIAN_BIO
        },
        'listener': {
            'username': settings.TEST_LISTENER_USERNAME,
            'email': settings.TEST_LISTENER_EMAIL,
            'password': settings.TEST_LISTENER_PASSWORD,
            'first_name': settings.TEST_LISTENER_FIRST_NAME,
            'last_name': settings.TEST_LISTENER_LAST_NAME,
            'role': 'listener'
        }
    }


def create_test_user_sql(db: Session, user_data: dict, user_type: str):
    """Create a test user using raw SQL"""
    # Check if user already exists
    result = db.execute(
        text("SELECT id, username, role FROM users WHERE username = :username OR email = :email"),
        {"username": user_data['username'], "email": user_data['email']}
    ).first()
    
    if result:
        # If user exists but has wrong role, update it
        if result.role != user_data['role']:
            db.execute(
                text("UPDATE users SET role = :role WHERE id = :id"),
                {"role": user_data['role'], "id": result.id}
            )
            db.commit()
            print(f"Updated {user_type.capitalize()} user '{user_data['username']}' role from '{result.role}' to '{user_data['role']}' (ID: {result.id})")
        else:
            print(f"{user_type.capitalize()} user '{user_data['username']}' already exists with correct role (ID: {result.id})")
        return result.id
    
    # Hash password
    hashed_password = hash_password(user_data['password'])
    now = datetime.now(timezone.utc)
    
    # Create user using SQL
    result = db.execute(
        text("""
        INSERT INTO users (username, email, password, first_name, last_name, role, created_at, is_active)
        VALUES (:username, :email, :password, :first_name, :last_name, :role, :created_at, :is_active)
        RETURNING id
        """),
        {
            "username": user_data['username'],
            "email": user_data['email'],
            "password": hashed_password,
            "first_name": user_data['first_name'],
            "last_name": user_data['last_name'],
            "role": user_data['role'],
            "created_at": now,
            "is_active": True
        }
    )
    
    user_id = result.scalar()
    db.commit()
    print(f"Created {user_type} user: {user_data['username']} (ID: {user_id})")
    return user_id


def create_test_artist_sql(db: Session, user_id: int, artist_data: dict):
    """Create a test artist profile using raw SQL"""
    # Check if artist profile already exists
    result = db.execute(
        text("SELECT id FROM artists WHERE linked_user_account = :user_id"),
        {"user_id": user_id}
    ).first()
    
    if result:
        print(f"Artist profile for user ID {user_id} already exists (ID: {result.id})")
        return result.id
    
    now = datetime.now(timezone.utc)
    
    # Create artist using SQL
    result = db.execute(
        text("""
        INSERT INTO artists (artist_stage_name, artist_bio, artist_profile_image, artist_social_link, 
                           linked_user_account, created_at, is_disabled)
        VALUES (:stage_name, :bio, :profile_image, :social_link, :user_id, :created_at, :is_disabled)
        RETURNING id
        """),
        {
            "stage_name": artist_data['stage_name'],
            "bio": artist_data['bio'],
            "profile_image": None,
            "social_link": None,
            "user_id": user_id,
            "created_at": now,
            "is_disabled": False
        }
    )
    
    artist_id = result.scalar()
    db.commit()
    print(f"Created artist profile: {artist_data['stage_name']} (ID: {artist_id})")
    return artist_id


def main():
    """Main seeding function"""
    print("Music Player API - User Seeding Script")
    print("=" * 50)
    
    # Load environment variables
    try:
        env_vars = load_env_vars()
        if env_vars is None:
            return
        print("Loaded environment variables from settings")
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        return
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create admin user
        print("\nCreating admin user...")
        admin_user_id = create_test_user_sql(db, env_vars['admin'], 'admin')
        
        # Create musician user
        print("\nCreating musician user...")
        musician_user_id = create_test_user_sql(db, env_vars['musician'], 'musician')
        
        # Create artist profile for musician
        print("\nCreating artist profile...")
        create_test_artist_sql(db, musician_user_id, env_vars['musician'])
        
        # Create listener user
        print("\nCreating listener user...")
        listener_user_id = create_test_user_sql(db, env_vars['listener'], 'listener')
        
        print("\n" + "=" * 50)
        print("Seeding completed successfully!")
        print("\nTest User Credentials:")
        print(f"Admin:     {env_vars['admin']['username']} / {env_vars['admin']['password']}")
        print(f"Musician:  {env_vars['musician']['username']} / {env_vars['musician']['password']}")
        print(f"Listener:  {env_vars['listener']['username']} / {env_vars['listener']['password']}")
        print("\nUse these credentials to test the API endpoints!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main() 
