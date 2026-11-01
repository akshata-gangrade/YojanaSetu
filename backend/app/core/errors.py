"""Centralized application exception types and consistent error responses."""

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.llm_client import (
    LLMAuthenticationError,
    LLMDailyCapExceededError,
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)


class ErrorDetail(BaseModel):
    """Structured error payload definition."""

    code: str
    message: str
    request_id: str | None = None
    details: Any = None


class ErrorResponse(BaseModel):
    """Consistent top-level API error envelope."""

    error: ErrorDetail


class AppException(Exception):
    """Base exception class for all domain-level application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Any = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedError(AppException):
    """Raised when authentication fails or credentials are missing."""

    def __init__(self, message: str = "Authentication required", details: Any = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenError(AppException):
    """Raised when authenticated user lacks required administrative privileges."""

    def __init__(self, message: str = "Access forbidden", details: Any = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class RateLimitExceededError(AppException):
    """Raised when client exceeds designated request rate limits."""

    def __init__(
        self, message: str = "Too many requests. Please slow down.", details: Any = None
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class PayloadTooLargeError(AppException):
    """Raised when incoming request body exceeds size limits."""

    def __init__(
        self, message: str = "Request payload exceeds allowed limit.", details: Any = None
    ):
        super().__init__(
            message=message,
            code="PAYLOAD_TOO_LARGE",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details=details,
        )


def _get_request_id(request: Request) -> str | None:
    """Safely retrieve request ID attached by middleware."""
    if hasattr(request, "state") and hasattr(request.state, "request_id"):
        return request.state.request_id
    return request.headers.get("x-request-id")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all domain exceptions with the consistent error envelope."""
    req_id = _get_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": req_id,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request schema validation errors consistently without leaking internal data."""
    req_id = _get_request_id(request)
    clean_errors = []
    for err in exc.errors():
        clean_errors.append(
            {
                "loc": err.get("loc"),
                "msg": err.get("msg"),
                "type": err.get("type"),
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the supplied fields.",
                "request_id": req_id,
                "details": clean_errors,
            }
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle standard Starlette/FastAPI HTTP exceptions with consistent error envelope."""
    req_id = _get_request_id(request)

    # Detect if Starlette body parser wrapped a PayloadTooLargeError
    cause = getattr(exc, "__cause__", None)
    if isinstance(cause, PayloadTooLargeError) or "byte limit" in str(exc.detail):
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "error": {
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": "Request body exceeds allowed limit.",
                    "request_id": req_id,
                    "details": None,
                }
            },
        )

    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        413: "PAYLOAD_TOO_LARGE",
        429: "RATE_LIMIT_EXCEEDED",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "request_id": req_id,
                "details": None,
            }
        },
    )


async def llm_exception_handler(request: Request, exc: LLMError) -> JSONResponse:
    """Map LLM-layer errors to safe, friendly client responses (429 or 503)."""
    req_id = _get_request_id(request)
    if isinstance(exc, LLMRateLimitError | LLMDailyCapExceededError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "AI service is currently busy or daily quota reached. Please try again later.",
                    "request_id": req_id,
                    "details": None,
                }
            },
        )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "code": "SERVICE_UNAVAILABLE",
                "message": "AI analysis service is temporarily unavailable. Please try again shortly.",
                "request_id": req_id,
                "details": None,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled internal server exceptions; never leaks stack traces."""
    req_id = _get_request_id(request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "request_id": req_id,
                "details": None,
            }
        },
    )
