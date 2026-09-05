"""Idempotently seed local/demo Q-Sign users from environment passwords."""

from __future__ import annotations

import os

from sqlalchemy import select

from api.auth import hash_password
from api.auth_models import UserRole
from api.database import SessionLocal, init_db
from api.user_models import User


DEMO_ACCOUNTS = (
    (
        "user",
        "user@qsign.local",
        UserRole.TRANSACTION_USER.value,
        "DEMO_USER_PASSWORD",
    ),
    (
        "operator",
        "operator@qsign.local",
        UserRole.SECURITY_OPERATOR.value,
        "DEMO_OPERATOR_PASSWORD",
    ),
)


def seed_demo_users() -> None:
    """Create missing demo accounts without printing passwords or hashes."""
    missing_variables = [
        password_variable
        for *_, password_variable in DEMO_ACCOUNTS
        if not os.getenv(password_variable, "")
    ]
    if missing_variables:
        names = ", ".join(missing_variables)
        raise RuntimeError(f"Set the required demo password variables: {names}")

    init_db()
    with SessionLocal() as database:
        for username, email, role, password_variable in DEMO_ACCOUNTS:
            existing = database.scalar(
                select(User).where(User.username == username)
            )
            if existing is not None:
                print(f"{username} ({role}): already exists")
                continue

            database.add(
                User(
                    username=username,
                    email=email,
                    password_hash=hash_password(os.environ[password_variable]),
                    role=role,
                )
            )
            database.commit()
            print(f"{username} ({role}): created")


if __name__ == "__main__":
    seed_demo_users()
