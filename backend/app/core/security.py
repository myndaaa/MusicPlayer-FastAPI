from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import jwt
from jwt import PyJWTError
from core.config import settings
from core.exceptions import PasswordVerificationError


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


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None,additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    Creates a JWT access token with expiry
    :param subject: Identifier to encode
    :param expires_delta: Token lifespan
    :param additional_claims: Extra data to include in payload 
    :return: JWT token string
    """

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        **(additional_claims or {})
    }
    # Encode JWT using your secret key
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str,expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token.
    :param subject: Identifier to encode
    :param expires_delta: Custom expiration time
    :return: JWT refresh token
    """

    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.refresh_token_expire_minutes))
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"  # distinguishes from access tokens
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    :param token: Encoded JWT token
    :return: Decoded payload as dictionary
    :raises: PyJWTError subclass (e.g., ExpiredSignatureError, InvalidTokenError)
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except PyJWTError as e:
        raise e
