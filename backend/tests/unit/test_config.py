"""Unit tests for typed Settings configuration and validation invariants."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_valid_development():
    """Verify development settings load properly with valid values."""
    settings = Settings(
        ENV="development",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="short_key_allowed_in_dev",
    )
    assert settings.ENV == "development"
    assert settings.MONGODB_DB == "yojanasetu"
    assert settings.ACCESS_TOKEN_MINUTES == 60


def test_settings_production_rejects_short_jwt_secret():
    """App must refuse to start if JWT_SECRET < 32 characters in production."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENV="production",
            MONGODB_URI="mongodb+srv://atlas.mongodb.net",
            MONGODB_DB="yojanasetu",
            GROQ_API_KEY="test_key",
            EMBEDDING_API_KEY="test_embed_key",
            JWT_SECRET="too_short_secret",
        )
    assert "JWT_SECRET must be at least 32 characters long in production" in str(
        exc_info.value
    )


def test_settings_production_accepts_valid_jwt_secret():
    """Verify production settings accept secrets of 32+ characters."""
    settings = Settings(
        ENV="production",
        MONGODB_URI="mongodb+srv://atlas.mongodb.net",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="a_very_secure_production_secret_key_exceeding_32_characters",
    )
    assert settings.ENV == "production"
    assert len(settings.JWT_SECRET) >= 32


def test_settings_allowed_origins_parsing():
    """Comma-separated origins string must parse into list of strings."""
    settings = Settings(
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="secret_key_placeholder_for_test",
        ALLOWED_ORIGINS="https://yojanasetu.in, https://admin.yojanasetu.in",
    )
    assert settings.ALLOWED_ORIGINS == [
        "https://yojanasetu.in",
        "https://admin.yojanasetu.in",
    ]
