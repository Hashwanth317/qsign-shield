"""Validated authentication request and response schemas."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(StrEnum):
    TRANSACTION_USER = "transaction_user"
    SECURITY_OPERATOR = "security_operator"


class AuthModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreate(AuthModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.TRANSACTION_USER

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        normalized = username.strip().lower()
        if not re.fullmatch(r"[a-z0-9_.-]+", normalized):
            raise ValueError(
                "Username may contain letters, numbers, dots, hyphens, and underscores."
            )
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: EmailStr) -> str:
        return str(email).lower()

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError("Password must not be blank.")
        return password


class UserLogin(AuthModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, username: str) -> str:
        return username.strip().lower()


class UserResponse(AuthModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class TokenResponse(AuthModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
