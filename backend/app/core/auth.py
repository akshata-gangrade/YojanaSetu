"""Administrative authentication and cryptographic security services.

Implements:
- Argon2id password hashing and constant-time verification using argon2-cffi
- Timing-attack mitigation with dummy verification for unregistered accounts
- Cryptographically signed short-lived JWT tokens (HS256, server-fixed algorithm)
- Token claim validation (sub, role, iat, exp, iss, jti)
"""

from datetime import UTC, datetime, timedelta
from typing import Any
import uuid

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
import jwt

from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.schemas.enums import AdminRole

# Argon2id password hasher (argon2-cffi defaults to Argon2id)
_ph = PasswordHasher()

# Precomputed valid Argon2id hash used strictly to equalize timing for non-existent accounts
_DUMMY_ARGON2ID_HASH = _ph.hash("timing_neutral_dummy_password_for_safety")

# Generic error message identical for wrong email and wrong password
GENERIC_LOGIN_ERROR = "Invalid email or password."


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id with default cryptographic salt."""
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against an Argon2id hash."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def run_dummy_password_verification(plain_password: str) -> None:
    """Execute a real Argon2id hash verification to prevent timing side-channels."""
    try:
        _ph.verify(_DUMMY_ARGON2ID_HASH, plain_password)
    except Exception:
        pass


def create_admin_jwt(
    email: str,
    role: AdminRole,
    expires_minutes: int | None = None,
    settings: Any | None = None,
) -> tuple[str, int]:
    """Generate a short-lived administrative JWT.

    Claims: sub, role, iat, exp, iss, jti.
    Algorithm is strictly fixed to HS256 on the server.
    Lifespan is capped at a maximum of 30 minutes.
    """
    cfg = settings or get_settings()
    now = datetime.now(UTC)

    # Expiry between 15 and 30 minutes, capped at 30 minutes
    configured_minutes = expires_minutes or cfg.ACCESS_TOKEN_MINUTES
    lifespan_minutes = max(15, min(configured_minutes, 30))
    exp_time = now + timedelta(minutes=lifespan_minutes)

    payload = {
        "sub": email.strip().lower(),
        "role": role.value if isinstance(role, AdminRole) else str(role),
        "iat": int(now.timestamp()),
        "exp": int(exp_time.timestamp()),
        "iss": cfg.JWT_ISSUER,
        "jti": uuid.uuid4().hex,
    }

    token = jwt.encode(payload, cfg.JWT_SECRET, algorithm="HS256")
    expires_in_seconds = lifespan_minutes * 60
    return token, expires_in_seconds


def decode_admin_jwt(token: str, settings: Any | None = None) -> dict[str, Any]:
    """Decode and strictly validate an admin JWT token.

    Invariants:
    - Algorithm is strictly enforced as HS256 (never read or trusted from token header).
    - Expiration and issuer are verified.
    - All required claims (sub, role, iat, exp, iss, jti) must be present.
    """
    cfg = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            cfg.JWT_SECRET,
            algorithms=["HS256"],
            issuer=cfg.JWT_ISSUER,
            options={
                "require": ["sub", "role", "iat", "exp", "iss", "jti"],
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            },
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Authentication token has expired.") from exc
    except (jwt.InvalidTokenError, jwt.PyJWTError) as exc:
        raise UnauthorizedError("Invalid authentication token.") from exc
