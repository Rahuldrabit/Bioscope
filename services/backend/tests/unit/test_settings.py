import pytest
from pydantic import ValidationError

from bioscope.bootstrap.settings import Settings


def test_invalid_database_url_is_rejected() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(database_url="not-a-database-url")


def test_numeric_confidence_cannot_be_enabled() -> None:
    with pytest.raises(ValidationError, match="ENABLE_NUMERIC_CONFIDENCE"):
        Settings(enable_numeric_confidence=True)


def test_production_demo_mode_is_rejected() -> None:
    with pytest.raises(ValidationError, match="DEMO_MODE"):
        Settings(app_env="production", demo_mode=True)


def test_production_rejects_local_dependency_defaults() -> None:
    with pytest.raises(ValidationError, match="localhost"):
        Settings(app_env="production", demo_mode=False)


def test_production_rejects_sqlite() -> None:
    with pytest.raises(ValidationError, match="require PostgreSQL"):
        Settings(
            app_env="production",
            demo_mode=False,
            database_url="sqlite+aiosqlite:///production.db",
            redis_url="rediss://cache.internal:6380/0",
            s3_endpoint="https://objects.example.com",
            s3_access_key_id="service-account",
            s3_secret_access_key="secret-from-vault",
        )


def test_production_accepts_remote_encrypted_dependencies() -> None:
    settings = Settings(
        app_env="production",
        demo_mode=False,
        database_url="postgresql+asyncpg://app:strong-password@db.internal/bioscope",
        redis_url="rediss://cache.internal:6380/0",
        s3_endpoint="https://objects.example.com",
        s3_access_key_id="service-account",
        s3_secret_access_key="secret-from-vault",
    )

    assert settings.app_env == "production"
