"""In-memory rate limiter baseline with per-minute window checking."""

import time
from collections import defaultdict

from fastapi import Request

from app.core.errors import RateLimitExceededError


class InMemoryRateLimiter:
    """Sliding window in-memory rate limiter per client IP."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.history: dict[str, list[float]] = defaultdict(list)

    def check(self, client_id: str) -> None:
        """Check if client has exceeded quota in the last 60 seconds."""
        now = time.time()
        window_start = now - 60.0

        # Discard expired timestamps
        timestamps = [ts for ts in self.history[client_id] if ts > window_start]
        self.history[client_id] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            raise RateLimitExceededError()

        self.history[client_id].append(now)


rate_limiter = InMemoryRateLimiter()


def rate_limit_dependency(request: Request) -> None:
    """FastAPI dependency to enforce rate limiting on sensitive routes."""
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)
