"""Authentication, password security, JWT, and role authorization tests."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from api.app import app
from api.auth import create_access_token, hash_password
from api.auth_models import UserRole
from api.database import Base, SessionLocal, engine, normalize_database_url
import api.database as database_module
from api.user_models import User


client = TestClient(app)
PASSWORD = "correct-horse-battery-staple"


@pytest.fixture(autouse=True)
def isolated_users() -> None:
    assert engine is not None
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register_transaction_user(
    *,
    username: str = "hashwanth",
    email: str = "hashwanth@example.com",
) -> dict:
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": PASSWORD,
            "role": "transaction_user",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_operator() -> User:
    with SessionLocal() as database:
        operator = User(
            username="operator",
            email="operator@example.com",
            password_hash=hash_password(PASSWORD),
            role=UserRole.SECURITY_OPERATOR.value,
        )
        database.add(operator)
        database.commit()
        database.refresh(operator)
        database.expunge(operator)
        return operator


def login(username: str = "hashwanth", password: str = PASSWORD):
    return client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )


def bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_user() -> None:
    user = register_transaction_user()
    assert user["username"] == "hashwanth"
    assert user["role"] == "transaction_user"
    assert "password" not in user
    assert "password_hash" not in user


def test_public_registration_defaults_to_transaction_user() -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "default-user",
            "email": "default@example.com",
            "password": PASSWORD,
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "transaction_user"


def test_duplicate_username_is_rejected() -> None:
    register_transaction_user()
    response = client.post(
        "/api/auth/register",
        json={
            "username": "hashwanth",
            "email": "another@example.com",
            "password": PASSWORD,
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username is already registered."


def test_duplicate_email_is_rejected() -> None:
    register_transaction_user()
    response = client.post(
        "/api/auth/register",
        json={
            "username": "another-user",
            "email": "hashwanth@example.com",
            "password": PASSWORD,
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered."


def test_password_is_stored_as_an_argon2_hash() -> None:
    register_transaction_user()
    with SessionLocal() as database:
        user = database.scalar(select(User).where(User.username == "hashwanth"))
        assert user is not None
        assert user.password_hash != PASSWORD
        assert user.password_hash.startswith("$argon2")


def test_valid_login_returns_token_and_safe_user() -> None:
    register_transaction_user()
    response = login()
    assert response.status_code == 200
    result = response.json()
    assert result["token_type"] == "bearer"
    assert result["access_token"]
    assert result["user"]["username"] == "hashwanth"
    assert "password_hash" not in result["user"]


def test_invalid_password_is_rejected() -> None:
    register_transaction_user()
    response = login(password="incorrect-password")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_inactive_user_cannot_log_in() -> None:
    register_transaction_user()
    with SessionLocal() as database:
        user = database.scalar(select(User).where(User.username == "hashwanth"))
        assert user is not None
        user.is_active = False
        database.commit()

    assert login().status_code == 401


def test_auth_me_without_token_is_rejected() -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_transaction_endpoint_without_token_is_rejected() -> None:
    response = client.post(
        "/api/sign",
        json={"sender": "Hashwanth", "message": "TRANSFER 10000 TO BOB"},
    )
    assert response.status_code == 401


def test_auth_me_with_token_returns_current_user() -> None:
    register_transaction_user()
    token = login().json()["access_token"]
    response = client.get("/api/auth/me", headers=bearer_headers(token))
    assert response.status_code == 200
    assert response.json()["username"] == "hashwanth"


def test_transaction_user_is_blocked_from_operator_endpoint() -> None:
    register_transaction_user()
    token = login().json()["access_token"]
    response = client.get("/api/quantum/status", headers=bearer_headers(token))
    assert response.status_code == 403
    assert response.json()["detail"] == "Security operator access is required."


def test_transaction_user_can_sign_and_verify_transaction() -> None:
    register_transaction_user()
    token = login().json()["access_token"]
    headers = bearer_headers(token)
    message = "TRANSFER 10000 TO BOB"

    signed_response = client.post(
        "/api/sign",
        headers=headers,
        json={"sender": "Hashwanth", "message": message},
    )
    assert signed_response.status_code == 201

    verification = client.post(
        "/api/verify",
        headers=headers,
        json={
            "message": message,
            "claimed_sender": "Hashwanth",
            "signature_id": signed_response.json()["signature_id"],
        },
    )
    assert verification.status_code == 200
    assert verification.json()["verification"] == "PASS"


def test_security_operator_can_access_operator_endpoint() -> None:
    create_operator()
    token = login(username="operator").json()["access_token"]
    response = client.get("/api/quantum/status", headers=bearer_headers(token))
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-valid-token",
        None,
    ],
)
def test_invalid_or_expired_token_is_rejected(token: str | None) -> None:
    user = create_operator()
    presented_token = token or create_access_token(
        user,
        expires_delta=timedelta(seconds=-1),
    )
    response = client.get(
        "/api/auth/me",
        headers=bearer_headers(presented_token),
    )
    assert response.status_code == 401


def test_public_registration_cannot_create_operator() -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "username": "operator",
            "email": "operator@example.com",
            "password": PASSWORD,
            "role": "security_operator",
        },
    )
    assert response.status_code == 403


def test_render_and_neon_postgres_urls_use_psycopg_driver() -> None:
    assert normalize_database_url(
        "postgres://user:pass@host/qsign"
    ) == "postgresql+psycopg://user:pass@host/qsign"
    assert normalize_database_url(
        "postgresql://user:pass@host/qsign?sslmode=require"
    ) == "postgresql+psycopg://user:pass@host/qsign?sslmode=require"


def test_database_unavailable_returns_clean_service_error(monkeypatch) -> None:
    monkeypatch.setattr(database_module, "engine", None)
    response = client.post(
        "/api/auth/register",
        json={
            "username": "offline-user",
            "email": "offline@example.com",
            "password": PASSWORD,
        },
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Authentication database is unavailable."
