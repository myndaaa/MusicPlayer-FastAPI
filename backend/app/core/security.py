from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from core.exception import JWTExpiredError, JWTDecodeError
from core.config import settings
from core.exception import PasswordVerificationError


# Argon2id hasher defaults
pwd_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,
    parallelism=2,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """
    Hash password with Argon2id + pepper.
    :param password: User's plain-text password
    :return: Secure hashed password to store in DB
    """
    # append pepper 
    peppered_password = password + settings.password_pepper
    return pwd_hasher.hash(peppered_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies password against the stored Argon2id hash.
    :param plain_password: Password user entered
    :param hashed_password: Hashed password from database
    :return: True if password is correct
    :raises: PasswordVerificationError if password does not match or verification fails
    """

    peppered_password = plain_password + settings.password_pepper
    try:
        # Returns True if match; raises error otherwise
        return pwd_hasher.verify(hashed_password, peppered_password)
    except argon2_exceptions.VerifyMismatchError:
        # Wrong password: raise exception
        raise PasswordVerificationError()
    except Exception as e:
        # unknown hashing errors, re-raise
        raise e

def create_access_token(subject: str, username: str, email: str, role: str, expires_delta: Optional[timedelta] = None, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Creates a JWT access token.
    Parameters:
    - subject: Unique identifier for token owner user_id
    - username: User's username
    - email: User's email
    - role: Role of the user (eg. admin, artist, listener)
    - expires_delta: Custom expiration duration (default: from settings)
    - additional_claims: Optional dict for extra fields

    Returns:
    - Signed JWT token string
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": subject, # token subject, user_id
        "exp": expire, # token expiry
        "iat": datetime.now(timezone.utc), # issued at timestamp
        "type": "access", # distinguish between access and refresh
        "username": username,
        "email": email,
        "role": role.lower(), # admin, artist, listener
        **(additional_claims or {}) # for future use 
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token.

    Parameters:
    - subject: Same as user ID
    - user_id: User's DB ID (can be used to revoke token via DB blacklist later)
    - expires_delta: custom expiry

    Returns:
    - Signed JWT refresh token string
    """
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.refresh_token_expire_minutes))
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh", # marks this token as a refresh token
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)



def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises custom exceptions for expired or invalid tokens.
    """
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError:
        raise JWTExpiredError()
    except InvalidTokenError:
        raise JWTDecodeError()
