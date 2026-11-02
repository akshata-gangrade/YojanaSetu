"""FastAPI application factory, middleware, and router registration."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.api.v1.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.errors import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    llm_exception_handler,
    validation_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.core.middleware import (
    RequestBodyLimitMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)
from app.db.mongo import MongoDBManager
from app.services.llm_client import LLMError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycles."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info("Starting YojanaSetu API (%s mode)", settings.ENV)

    # Initialize DB client inside the running event loop
    MongoDBManager.get_client()

    yield

    logger.info("Shutting down YojanaSetu API, closing DB connections...")
    await MongoDBManager.close_client()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application instance."""
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="YojanaSetu API",
        description=(
            "Backend API for YojanaSetu - AI-powered scheme navigator for India."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.ENABLE_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_DOCS else None,
        openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
        lifespan=lifespan,
    )

    # 1. CORS Allowlist: exact origins only, strictly avoiding wildcards
    raw_origins = (
        settings.ALLOWED_ORIGINS
        if isinstance(settings.ALLOWED_ORIGINS, list)
        else [settings.ALLOWED_ORIGINS]
    )
    exact_origins = [o.strip() for o in raw_origins if o.strip() and o.strip() != "*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=exact_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Defensive Security and Request Limits
    app.add_middleware(RequestBodyLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # 3. Centralized exception handlers for consistent API error contracts
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(LLMError, llm_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # 4. Mount health endpoint at root /health for container orchestrators
    app.include_router(health_router)

    # 5. Mount versioned API routes
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
