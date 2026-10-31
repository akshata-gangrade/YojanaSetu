"""In-memory rate limiter with per-minute sliding window, memory eviction, and proxy-aware IP detection."""

from collections import defaultdict
import time

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import RateLimitExceededError


class InMemoryRateLimiter:
    """Sliding window in-memory rate limiter per client IP and action bucket.

    Evicts expired entries outside the sliding window so memory cannot grow without bound.
    """

    def __init__(self, default_rpm: int = 60):
        self.default_rpm = default_rpm
        self.history: dict[str, list[float]] = defaultdict(list)
        self._check_counter: int = 0

    def check(
        self, client_id: str, max_requests: int | None = None, bucket: str = "default"
    ) -> None:
        """Check if client has exceeded quota in the sliding 60-second window."""
        limit = max_requests if max_requests is not None else self.default_rpm
        now = time.time()
        window_start = now - 60.0

        key = f"{client_id}:{bucket}"
        timestamps = [ts for ts in self.history[key] if ts > window_start]

        if timestamps:
            self.history[key] = timestamps
        else:
            # Evict key if all timestamps expired
            self.history.pop(key, None)

        if len(timestamps) >= limit:
            raise RateLimitExceededError(
                message=f"Rate limit exceeded ({limit} requests/min). Please try again shortly."
            )

        self.history[key].append(now)

        # Periodically evict stale keys from inactive clients to prevent memory growth
        self._check_counter += 1
        if self._check_counter >= 100:
            self._check_counter = 0
            self.cleanup_expired(now)

    def cleanup_expired(self, now: float | None = None) -> int:
        """Evict all client entries older than the sliding window so memory cannot grow without bound.

        Returns:
            Number of evicted client bucket keys.
        """
        current_time = now if now is not None else time.time()
        window_start = current_time - 60.0

        expired_keys = [
            k
            for k, timestamps in list(self.history.items())
            if not timestamps or timestamps[-1] <= window_start
        ]

        for k in expired_keys:
            self.history.pop(k, None)

        return len(expired_keys)

    def reset(self) -> None:
        """Clear all rate limit history (useful for test isolation)."""
        self.history.clear()
        self._check_counter = 0


rate_limiter = InMemoryRateLimiter()


def get_client_ip(request: Request) -> str:
    """Determine client IP securely depending on deployment environment.

    - In development (ENV != 'production'): uses socket address (request.client.host)
      so a client cannot forge X-Forwarded-For headers to bypass rate limits.
    - In production (ENV == 'production') behind Render's reverse proxy:
      uses the rightmost IP address added by the trusted proxy in X-Forwarded-For,
      preventing client-prepended spoofed addresses from bypassing limits.
    """
    settings = get_settings()

    if settings.ENV == "production":
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Render appends the real client IP to the end of the X-Forwarded-For chain
            ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
            if ips:
                return ips[-1]

    # In development, use socket peer address exclusively (unforgeable by client header)
    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


def rate_limit_dependency(request: Request) -> None:
    """Default per-IP rate limit dependency based on RATE_LIMIT_PER_MINUTE."""
    settings = get_settings()
    ip = get_client_ip(request)
    rate_limiter.check(
        client_id=ip,
        max_requests=settings.RATE_LIMIT_PER_MINUTE,
        bucket="default",
    )


def rate_limit_intake_dependency(request: Request) -> None:
    """Strict rate limit on intake extraction: exactly a quarter of RATE_LIMIT_PER_MINUTE (lower, not higher)."""
    settings = get_settings()
    ip = get_client_ip(request)
    quarter_limit = max(1, settings.RATE_LIMIT_PER_MINUTE // 4)
    rate_limiter.check(
        client_id=ip,
        max_requests=quarter_limit,
        bucket="intake_extract",
    )


def rate_limit_ask_dependency(request: Request) -> None:
    """Strict rate limit on scheme Q&A: exactly a quarter of RATE_LIMIT_PER_MINUTE (lower, not higher)."""
    settings = get_settings()
    ip = get_client_ip(request)
    quarter_limit = max(1, settings.RATE_LIMIT_PER_MINUTE // 4)
    rate_limiter.check(
        client_id=ip,
        max_requests=quarter_limit,
        bucket="scheme_ask",
    )
