from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MusicStreamer"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"

    # Server
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    # Database
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  

    # Password pepper
    PASSWORD_PEPPER: str

    # Email Configuration
    EMAIL_PROVIDER: str = "sendgrid"  # console, sendgrid, gmail
    SENDGRID_API_KEY: Optional[str] = None
    GMAIL_USERNAME: Optional[str] = None
    GMAIL_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "mysha.shemontee@monstar-lab.com"
    VERIFICATION_BASE_URL: str = "http://localhost:8000/auth/verify-email"

    # Test User Credentials (optional, only for development)
    TEST_ADMIN_USERNAME: Optional[str] = None
    TEST_ADMIN_EMAIL: Optional[str] = None
    TEST_ADMIN_PASSWORD: Optional[str] = None
    TEST_ADMIN_FIRST_NAME: Optional[str] = None
    TEST_ADMIN_LAST_NAME: Optional[str] = None

    TEST_MUSICIAN_USERNAME: Optional[str] = None
    TEST_MUSICIAN_EMAIL: Optional[str] = None
    TEST_MUSICIAN_PASSWORD: Optional[str] = None
    TEST_MUSICIAN_FIRST_NAME: Optional[str] = None
    TEST_MUSICIAN_LAST_NAME: Optional[str] = None
    TEST_MUSICIAN_STAGE_NAME: Optional[str] = None
    TEST_MUSICIAN_BIO: Optional[str] = None

    TEST_LISTENER_USERNAME: Optional[str] = None
    TEST_LISTENER_EMAIL: Optional[str] = None
    TEST_LISTENER_PASSWORD: Optional[str] = None
    TEST_LISTENER_FIRST_NAME: Optional[str] = None
    TEST_LISTENER_LAST_NAME: Optional[str] = None

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow" 

settings = Settings()

