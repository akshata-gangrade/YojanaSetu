"""Global test fixtures and environment overrides."""

import os

# Inject required test environment variables before app imports
os.environ["ENV"] = "development"
os.environ["API_PREFIX"] = "/api/v1"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB"] = "yojanasetu_test"
os.environ["GROQ_API_KEY"] = "gsk_dummy_test_key"
os.environ["GROQ_MODEL"] = "llama-3.3-70b-versatile"
os.environ["EMBEDDING_PROVIDER"] = "hosted"
os.environ["EMBEDDING_API_KEY"] = "dummy_embedding_test_key"
os.environ["EMBEDDING_MODEL"] = "hosted-multilingual-e5"
os.environ["EMBEDDING_DIM"] = "384"
os.environ["JWT_SECRET"] = "super_secret_test_jwt_key_that_is_long_enough"
os.environ["JWT_ISSUER"] = "yojanasetu"
os.environ["ACCESS_TOKEN_MINUTES"] = "60"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173,http://localhost:3000"
os.environ["ENABLE_DOCS"] = "true"
os.environ["RATE_LIMIT_PER_MINUTE"] = "60"
os.environ["LLM_DAILY_CALL_CAP"] = "1000"
os.environ["SIMILARITY_THRESHOLD"] = "0.7"
os.environ["LOG_LEVEL"] = "INFO"

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.core.config import Settings, get_settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture(autouse=True)
def isolate_settings_env(monkeypatch: pytest.MonkeyPatch):
    """Isolate tests from ambient env variables and clear Settings cache."""
    get_settings.cache_clear()
    for field_name in Settings.model_fields.keys():
        monkeypatch.delenv(field_name, raising=False)
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_settings() -> Settings:
    """Return explicit Settings instance for testing."""
    return Settings(
        _env_file=None,
        ENV="development",
        API_PREFIX="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu_test",
        GROQ_API_KEY="gsk_dummy_test_key",
        GROQ_MODEL="llama-3.3-70b-versatile",
        EMBEDDING_PROVIDER="hosted",
        EMBEDDING_API_KEY="dummy_embedding_test_key",
        EMBEDDING_MODEL="hosted-multilingual-e5",
        EMBEDDING_DIM=384,
        JWT_SECRET="super_secret_test_jwt_key_that_is_long_enough",
        JWT_ISSUER="yojanasetu",
        ACCESS_TOKEN_MINUTES=60,
        ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"],
        ENABLE_DOCS=True,
        RATE_LIMIT_PER_MINUTE=60,
        LLM_DAILY_CALL_CAP=1000,
        SIMILARITY_THRESHOLD=0.7,
        LOG_LEVEL="INFO",
        INCLUDE_SAMPLE_SCHEMES=False,
    )


@pytest.fixture
async def async_client(test_settings: Settings) -> AsyncClient:
    """Async test client using ASGITransport."""
    app = create_app(test_settings)
    app.dependency_overrides[get_settings] = lambda: test_settings
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
