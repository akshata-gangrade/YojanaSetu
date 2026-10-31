"""FastAPI application factory, middleware, and router registration."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.api.v1.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.errors import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.db.mongo import MongoDBManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycles."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info("Starting YojanaSetu API (%s mode)", settings.ENV)

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

    # Cross-Origin Resource Sharing (CORS) Allowlist
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Centralized exception handlers for consistent API error contracts
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Mount health endpoint at root /health for container orchestrators
    app.include_router(health_router)

    # Mount versioned API routes
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
