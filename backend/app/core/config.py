from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "MusicStreamer"
    app_env: str = "development"
    app_version: str = "1.0.0"

    # Server
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    # Database
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_server: str = "localhost"
    postgres_port: int = 5432

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 43200  

    # Password pepper
    password_pepper: str

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  

settings = Settings()

