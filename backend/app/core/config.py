"""Typed application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the API and its external services."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="AI Eye Disease Detection API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, ge=1, le=65535, alias="PORT")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    mongodb_uri: str | None = Field(default=None, alias="MONGODB_URI")
    mongodb_database: str = Field(default="eye_disease_detection", alias="MONGODB_DATABASE")
    mongodb_server_selection_timeout_ms: int = Field(
        default=10_000,
        ge=1_000,
        alias="MONGODB_SERVER_SELECTION_TIMEOUT_MS",
    )

    jwt_secret_key: str | None = Field(default=None, alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def cors_origins(self) -> list[str]:
        """Return normalized browser origins allowed by CORS."""
        return [
            origin.strip()
            for origin in self.cors_origins_raw.split(",")
            if origin.strip()
        ]

    def require_mongodb_uri(self) -> str:
        """Return the MongoDB URI or fail fast during application startup."""
        if not self.mongodb_uri:
            raise RuntimeError("MONGODB_URI environment variable is required.")
        return self.mongodb_uri

    def require_jwt_secret(self) -> str:
        """Return the JWT secret or fail safely before token use."""
        if not self.jwt_secret_key:
            raise RuntimeError("JWT_SECRET_KEY environment variable is required.")
        return self.jwt_secret_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide immutable application settings instance."""
    return Settings()

