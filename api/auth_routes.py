"""Registration, login, and current-user endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from api.auth_models import TokenResponse, UserCreate, UserLogin, UserResponse, UserRole
from api.database import get_db
from api.user_models import User


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _operator_registration_enabled() -> bool:
    return os.getenv("ALLOW_OPERATOR_REGISTRATION", "false").lower() in {
        "1",
        "true",
        "yes",
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(request: UserCreate, database: Session = Depends(get_db)) -> User:
    """Create a transaction user; operator registration is disabled by default."""
    if (
        request.role == UserRole.SECURITY_OPERATOR
        and not _operator_registration_enabled()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security operator accounts must be created by an administrator.",
        )

    if database.scalar(select(User.id).where(User.username == request.username)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already registered.",
        )
    if database.scalar(select(User.id).where(User.email == str(request.email))):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )

    user = User(
        username=request.username,
        email=str(request.email),
        password_hash=hash_password(request.password),
        role=request.role.value,
    )
    database.add(user)
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered.",
        ) from error
    database.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(request: UserLogin, database: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate an active user and issue a signed JWT access token."""
    user = database.scalar(select(User).where(User.username == request.username))
    if (
        user is None
        or not user.is_active
        or not verify_password(request.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = create_access_token(user)
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured.",
        ) from error

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user without exposing the password hash."""
    return current_user
