"""Password hashing, JWT creation, and FastAPI authorization dependencies."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.auth_models import UserRole
from api.database import DATABASE_UNAVAILABLE_MESSAGE, get_db
from api.user_models import User


password_hasher = PasswordHasher()
bearer_scheme = HTTPBearer(auto_error=False)
SUPPORTED_JWT_ALGORITHMS = {"HS256", "HS384", "HS512"}


def hash_password(password: str) -> str:
    """Hash a password with Argon2id; plaintext is never persisted."""
    if not password:
        raise ValueError("Password must not be empty.")
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely compare plaintext input with an Argon2 password hash."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerificationError, InvalidHashError):
        return False


def _jwt_settings() -> tuple[str, str, int]:
    secret_key = os.getenv("JWT_SECRET_KEY", "").strip()
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not configured.")
    if len(secret_key) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 characters.")

    algorithm = os.getenv("JWT_ALGORITHM", "HS256").strip().upper()
    if algorithm not in SUPPORTED_JWT_ALGORITHMS:
        raise RuntimeError("JWT_ALGORITHM must use a supported HMAC algorithm.")

    try:
        expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    except ValueError as error:
        raise RuntimeError(
            "ACCESS_TOKEN_EXPIRE_MINUTES must be an integer."
        ) from error
    if expire_minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive.")
    return secret_key, algorithm, expire_minutes


def create_access_token(
    user: User,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed access token containing the user identity and role."""
    secret_key, algorithm, expire_minutes = _jwt_settings()
    now = datetime.now(UTC)
    expires_at = now + (expires_delta or timedelta(minutes=expire_minutes))
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT using only the configured algorithm."""
    secret_key, algorithm, _ = _jwt_settings()
    return jwt.decode(token, secret_key, algorithms=[algorithm])


def _authentication_error(detail: str = "Could not validate credentials.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    database: Session = Depends(get_db),
) -> User:
    """Return the active database user represented by a valid bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _authentication_error()

    try:
        payload = decode_access_token(credentials.credentials)
    except ExpiredSignatureError as error:
        raise _authentication_error("Authentication token has expired.") from error
    except InvalidTokenError as error:
        raise _authentication_error() from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured.",
        ) from error

    subject = payload.get("sub")
    token_role = payload.get("role")
    if not isinstance(subject, str) or not subject.isdigit():
        raise _authentication_error()

    try:
        user = database.scalar(select(User).where(User.id == int(subject)))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_UNAVAILABLE_MESSAGE,
        ) from error

    if user is None or token_role != user.role:
        raise _authentication_error()
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )
    return user


def require_security_operator(
    current_user: User = Depends(get_current_user),
) -> User:
    """Restrict sensitive monitoring and simulation routes to operators."""
    if current_user.role != UserRole.SECURITY_OPERATOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security operator access is required.",
        )
    return current_user
