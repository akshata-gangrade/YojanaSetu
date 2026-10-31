"""Security, logging, request tracking, and request size middleware."""

from collections.abc import Callable
import json
import logging
import time
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.errors import PayloadTooLargeError

logger = logging.getLogger("yojanasetu.access")

# 32 KB maximum request body payload limit for JSON routes
MAX_REQUEST_BODY_BYTES = 32 * 1024


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns or propagates unique request IDs across the request lifecycle."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = request.headers.get("x-request-id")
        if not req_id or len(req_id) > 64:
            req_id = uuid.uuid4().hex

        request.state.request_id = req_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces essential defensive HTTP security headers on all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response


class RequestBodyLimitMiddleware:
    """ASGI middleware bounding maximum allowed payload size to 32 KB.

    Counts actual received bytes across both Content-Length and chunked transfer streams.
    """

    def __init__(self, app: ASGIApp, max_bytes: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. Fast-path Content-Length header check
        headers = dict(scope.get("headers", []))
        content_length_raw = headers.get(b"content-length")
        state = scope.get("state", {})
        req_id = state.get("request_id")
        if not req_id:
            req_id_raw = headers.get(b"x-request-id")
            req_id = req_id_raw.decode("latin1") if req_id_raw else uuid.uuid4().hex

        if content_length_raw:
            try:
                length = int(content_length_raw.decode("latin1"))
                if length > self.max_bytes:
                    response = JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": f"Request body exceeds {self.max_bytes} byte limit.",
                                "request_id": req_id,
                                "details": None,
                            }
                        },
                        headers={"X-Request-ID": req_id},
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass

        # 2. Intercept receive to count actual received bytes (supports chunked bodies)
        bytes_received = 0

        async def limited_receive():
            nonlocal bytes_received
            message = await receive()
            if message.get("type") == "http.request":
                chunk = message.get("body", b"")
                bytes_received += len(chunk)
                if bytes_received > self.max_bytes:
                    raise PayloadTooLargeError(
                        message=f"Request body exceeds {self.max_bytes} byte limit."
                    )
            return message

        try:
            await self.app(scope, limited_receive, send)
        except PayloadTooLargeError:
            response = JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request body exceeds {self.max_bytes} byte limit.",
                        "request_id": req_id,
                        "details": None,
                    }
                },
                headers={"X-Request-ID": req_id},
            )
            await response(scope, receive, send)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Emits structured JSON logs for HTTP access.

    Invariant: Strictly never logs citizen message text, user profile attributes,
    or personal identifiers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        req_id = getattr(request.state, "request_id", None)
        client_ip = request.client.host if request.client else "unknown"

        # Safe metadata only: method, path, status, duration, request_id
        log_entry = {
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        }
        logger.info(json.dumps(log_entry))

        return response
