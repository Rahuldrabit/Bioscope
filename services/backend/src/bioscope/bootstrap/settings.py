"""Validated, environment-backed application configuration."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Runtime settings with safe local defaults and production guards."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    demo_mode: bool = True
    database_url: str = "postgresql+asyncpg://bioscope:bioscope@localhost:5432/bioscope"
    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "bioscope-private"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    api_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    enable_external_sources: bool = False
    enable_skin_image_upload: bool = False
    enable_numeric_confidence: bool = False
    max_upload_mb: int = Field(default=10, ge=1, le=100)
    asset_retention_days: int = Field(default=7, ge=1, le=365)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        try:
            url = make_url(value)
        except Exception as exc:  # pragma: no cover - SQLAlchemy owns parsing detail.
            raise ValueError("DATABASE_URL must be a valid SQLAlchemy URL") from exc
        if url.drivername not in {"postgresql+asyncpg", "sqlite+aiosqlite"}:
            raise ValueError(
                "DATABASE_URL must use postgresql+asyncpg (or sqlite+aiosqlite in local tests)"
            )
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
            raise ValueError("REDIS_URL must use redis:// or rediss:// and include a host")
        return value

    @field_validator("s3_endpoint")
    @classmethod
    def validate_s3_endpoint(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("S3_ENDPOINT must use http:// or https:// and include a host")
        return value

    @model_validator(mode="after")
    def validate_runtime_safety(self) -> Settings:
        if self.app_env in {"staging", "production"}:
            if self.demo_mode:
                raise ValueError("DEMO_MODE must be false outside local environments")

            database = make_url(self.database_url)
            redis = urlparse(self.redis_url)
            s3 = urlparse(self.s3_endpoint)
            local_hosts = {"localhost", "127.0.0.1", "::1"}
            if database.drivername != "postgresql+asyncpg":
                raise ValueError("Staging and production require PostgreSQL")
            dependency_hosts = {database.host, redis.hostname, s3.hostname}
            if dependency_hosts & local_hosts:
                raise ValueError("Staging and production dependencies cannot use localhost")
            if {database.username, database.password} & {"bioscope"}:
                raise ValueError(
                    "Default database credentials are forbidden outside local environments"
                )
            if self.app_env == "production" and s3.scheme != "https":
                raise ValueError("S3_ENDPOINT must use HTTPS in production")
            if {self.s3_access_key_id, self.s3_secret_access_key} & {"minioadmin"}:
                raise ValueError("Default S3 credentials are forbidden outside local environments")
        if self.enable_numeric_confidence:
            raise ValueError(
                "ENABLE_NUMERIC_CONFIDENCE is unavailable until calibration is validated"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process configuration once; tests instantiate Settings directly."""

    return Settings()
