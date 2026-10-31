"""Security helpers: password hashing, token encoding, and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify raw password against bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    secret_key: str,
    issuer: str = "yojanasetu",
    expires_delta: timedelta | None = None,
) -> str:
    """Encode a signed JWT access token for administrative sessions."""
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=60)

    payload: dict[str, Any] = {
        "sub": subject,
        "iss": issuer,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_access_token(
    token: str, secret_key: str, issuer: str = "yojanasetu"
) -> dict[str, Any]:
    """Verify and decode a signed JWT token."""
    return jwt.decode(
        token,
        secret_key,
        algorithms=[ALGORITHM],
        issuer=issuer,
    )
