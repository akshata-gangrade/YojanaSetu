"""Unit tests for typed Settings configuration and validation invariants."""

import os

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_settings_valid_development():
    """Verify development settings load properly and ignore local .env."""
    settings = Settings(
        _env_file=None,
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
    assert settings.INCLUDE_SAMPLE_SCHEMES is False
    assert settings.PUBLISH_UNREVIEWED_SCHEMES is True


def test_settings_production_allows_publish_unreviewed_schemes():
    """Verify production mode allows PUBLISH_UNREVIEWED_SCHEMES (no production restriction)."""
    settings = Settings(
        _env_file=None,
        ENV="production",
        MONGODB_URI="mongodb+srv://atlas.mongodb.net",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="a_very_secure_production_secret_key_exceeding_32_characters",
        PUBLISH_UNREVIEWED_SCHEMES=True,
    )
    assert settings.PUBLISH_UNREVIEWED_SCHEMES is True


def test_settings_development_allows_publish_unreviewed_schemes():
    """Verify development mode permits toggling PUBLISH_UNREVIEWED_SCHEMES."""
    settings = Settings(
        _env_file=None,
        ENV="development",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="dev_secret_key",
        PUBLISH_UNREVIEWED_SCHEMES=False,
    )
    assert settings.PUBLISH_UNREVIEWED_SCHEMES is False


def test_settings_production_rejects_include_sample_schemes():
    """Fail fast: Settings validation fails if INCLUDE_SAMPLE_SCHEMES=True in prod."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
            ENV="production",
            MONGODB_URI="mongodb+srv://atlas.mongodb.net",
            MONGODB_DB="yojanasetu",
            GROQ_API_KEY="test_key",
            EMBEDDING_API_KEY="test_embed_key",
            JWT_SECRET="a_very_secure_production_secret_key_exceeding_32_characters",
            INCLUDE_SAMPLE_SCHEMES=True,
        )
    assert "INCLUDE_SAMPLE_SCHEMES must be False in production" in str(exc_info.value)


def test_settings_development_allows_include_sample_schemes():
    """Verify development mode permits INCLUDE_SAMPLE_SCHEMES=True for testing."""
    settings = Settings(
        _env_file=None,
        ENV="development",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="dev_secret_key",
        INCLUDE_SAMPLE_SCHEMES=True,
    )
    assert settings.INCLUDE_SAMPLE_SCHEMES is True


def test_settings_production_rejects_short_jwt_secret():
    """App must refuse to start if JWT_SECRET < 32 characters in production."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            _env_file=None,
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
        _env_file=None,
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
        _env_file=None,
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


def test_settings_isolated_from_process_environment(monkeypatch: pytest.MonkeyPatch):
    """Prove isolation: outer process env and local .env cannot bleed into Settings.

    Even if INCLUDE_SAMPLE_SCHEMES='true' is set in the outer process environment,
    the conftest autouse fixture strips it, and passing _env_file=None prevents reading
    the local .env file. Thus, building Settings without an explicit value resolves
    cleanly to the default (False).
    """
    # 1. Simulate an external process setting INCLUDE_SAMPLE_SCHEMES=true
    monkeypatch.setenv("INCLUDE_SAMPLE_SCHEMES", "true")
    assert os.environ.get("INCLUDE_SAMPLE_SCHEMES") == "true"

    # 2. Simulate what the autouse fixture does before every test:
    for field_name in Settings.model_fields.keys():
        monkeypatch.delenv(field_name, raising=False)
    get_settings.cache_clear()

    # 3. Build Settings with _env_file=None and no explicit value for sample schemes
    settings = Settings(
        _env_file=None,
        ENV="development",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu",
        GROQ_API_KEY="test_key",
        EMBEDDING_API_KEY="test_embed_key",
        JWT_SECRET="dev_secret_key",
    )

    # 4. Proves isolation: not influenced by local .env or process env
    assert settings.INCLUDE_SAMPLE_SCHEMES is False
