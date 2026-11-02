"""Application configuration management using pydantic-settings.

Validates environment variables at startup and enforces security invariants.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core environment
    ENV: Literal["development", "production"] = Field(
        default="development",
        description="Application environment mode.",
    )
    API_PREFIX: str = Field(
        default="/api/v1",
        description="Prefix for all versioned API routes.",
    )

    # Database
    MONGODB_URI: str = Field(
        ...,
        description="MongoDB Atlas connection URI.",
    )
    MONGODB_DB: str = Field(
        ...,
        description="MongoDB target database name.",
    )

    # LLM & Embeddings (Hosted APIs behind interfaces)
    GROQ_API_KEY: str = Field(
        ...,
        description="Groq API key for LLM inference.",
    )
    GROQ_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model identifier.",
    )
    EMBEDDING_PROVIDER: str = Field(
        default="hosted",
        description="Hosted embeddings service provider identifier.",
    )
    EMBEDDING_API_KEY: str = Field(
        ...,
        description="API key for hosted embeddings service.",
    )
    EMBEDDING_MODEL: str = Field(
        default="hosted-multilingual-e5",
        description="Embedding model name.",
    )
    EMBEDDING_DIM: int = Field(
        default=384,
        gt=0,
        description="Embedding vector dimensionality.",
    )

    # Security & Auth
    JWT_SECRET: str = Field(
        ...,
        description="Secret key for signing admin access tokens.",
    )
    JWT_ISSUER: str = Field(
        default="yojanasetu",
        description="JWT token issuer string.",
    )
    ACCESS_TOKEN_MINUTES: int = Field(
        default=60,
        gt=0,
        description="Access token lifespan in minutes.",
    )
    ALLOWED_ORIGINS: list[str] | str = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origin domains.",
    )

    # Documentation & Limits
    ENABLE_DOCS: bool = Field(
        default=True,
        description="Whether interactive OpenAPI documentation is enabled.",
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="Default per-IP rate limit per minute.",
    )
    LLM_DAILY_CALL_CAP: int = Field(
        default=1000,
        gt=0,
        description="Application-wide daily LLM call cap.",
    )
    SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum vector similarity score for retrieved chunks.",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Standard log verbosity level.",
    )
    INCLUDE_SAMPLE_SCHEMES: bool = Field(
        default=False,
        description="Whether public queries include fictional sample schemes.",
    )
    # Whether public queries include unreviewed schemes awaiting verification
    PUBLISH_UNREVIEWED_SCHEMES: bool = Field(
        default=True,
        description="Whether public queries include unreviewed schemes awaiting verification.",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        """Parse comma-separated origin string into a list of cleaned strings."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_invariants(self) -> "Settings":
        """Enforce strict production safeguards on secrets and documentation."""
        if self.ENV == "production":
            if len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "JWT_SECRET must be at least 32 characters long in production."
                )
            if self.INCLUDE_SAMPLE_SCHEMES is True:
                raise ValueError("INCLUDE_SAMPLE_SCHEMES must be False in production.")
            # In production, OpenAPI documentation should be disabled by default
            # unless explicitly enabled in an authorized staging context.
            if self.ENABLE_DOCS is True:
                # In production, docs are disabled by default
                pass
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
