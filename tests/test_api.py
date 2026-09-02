"""FastAPI integration tests for Q-Sign Shield V0.6."""

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.routes import reset_api_state


client = TestClient(app)
MESSAGE = "TRANSFER 10000 TO BOB"
FORGED_MESSAGE = "TRANSFER 90000 TO BOB"


@pytest.fixture(autouse=True)
def isolated_api_state() -> None:
    reset_api_state()
    yield
    reset_api_state()


def sign_message() -> dict:
    response = client.post(
        "/api/sign",
        json={"message": MESSAGE, "sender": "Alice"},
    )
    assert response.status_code == 201
    return response.json()


def transaction_payload(signed: dict, **overrides: str) -> dict:
    payload = {
        "message": MESSAGE,
        "claimed_sender": "Alice",
        "signature_id": signed["signature_id"],
    }
    payload.update(overrides)
    return payload


def test_root_returns_api_information() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "project": "Q-Sign Shield",
        "version": "0.6",
        "status": "running",
    }


def test_health_returns_healthy() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_swagger_and_redoc_are_available() -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_legitimate_message_can_be_signed() -> None:
    signed = sign_message()
    assert signed["status"] == "SIGNED"
    assert signed["signature_owner"] == "Alice"
    assert signed["signature_id"].startswith("QS-")
    assert len(signed["signature_fingerprint"]) == 16
    assert signed["message_hash"].endswith("...")


def test_legitimate_signed_transaction_verifies() -> None:
    signed = sign_message()
    response = client.post("/api/verify", json=transaction_payload(signed))
    assert response.status_code == 200
    result = response.json()
    assert result["verification"] == "PASS"
    assert result["security_decision"] == "LEGITIMATE"
    assert result["matching_bits"] == result["total_bits"] == 16
    assert result["identity_match"] is True


def test_forged_message_is_blocked() -> None:
    signed = sign_message()
    response = client.post(
        "/api/security/check",
        json=transaction_payload(signed, message=FORGED_MESSAGE),
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "BLOCKED"
    assert result["attack_type"] == "FORGERY"
    assert result["security_decision"] == "FORGERY ATTACK DETECTED"


def test_tampered_signature_is_blocked() -> None:
    signed = sign_message()
    original = signed["signature_fingerprint"]
    tampered = "".join(
        ("1" if bit == "0" else "0") if index < 2 else bit
        for index, bit in enumerate(original)
    )
    response = client.post(
        "/api/security/check",
        json=transaction_payload(signed, signature_bits=tampered),
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "BLOCKED"
    assert result["attack_type"] == "SIGNATURE_TAMPERING"
    assert result["mismatching_bits"] == 2


def test_impersonation_is_blocked_but_signature_remains_valid() -> None:
    signed = sign_message()
    response = client.post(
        "/api/security/check",
        json=transaction_payload(signed, claimed_sender="Attacker"),
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "BLOCKED"
    assert result["attack_type"] == "IMPERSONATION"
    assert result["cryptographic_signature"] == "PASS"
    assert result["identity_match"] is False
    assert result["overall_verification"] == "FAIL"


def test_replay_is_detected_on_second_use() -> None:
    signed = sign_message()
    payload = transaction_payload(signed)
    first = client.post("/api/security/check", json=payload)
    second = client.post("/api/security/check", json=payload)

    assert first.status_code == second.status_code == 200
    assert first.json()["status"] == "ACCEPTED"
    assert first.json()["attack_detected"] is False
    assert second.json()["status"] == "BLOCKED"
    assert second.json()["attack_type"] == "REPLAY"
    assert second.json()["security_decision"] == "REPLAY ATTACK DETECTED"


def test_unknown_signature_id_returns_not_found() -> None:
    response = client.post(
        "/api/verify",
        json={
            "message": MESSAGE,
            "claimed_sender": "Alice",
            "signature_id": "QS-NOTFOUND",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.parametrize(
    "path,payload",
    [
        ("/api/sign", {"message": "", "sender": "Alice"}),
        ("/api/sign", {"message": MESSAGE, "sender": ""}),
        ("/api/verify", {}),
    ],
)
def test_empty_or_invalid_requests_are_rejected(path: str, payload: dict) -> None:
    response = client.post(path, json=payload)
    assert response.status_code == 422


def test_unknown_signer_cannot_generate_signature() -> None:
    response = client.post(
        "/api/sign",
        json={"message": MESSAGE, "sender": "Attacker"},
    )
    assert response.status_code == 400
    assert "Unknown signer" in response.json()["detail"]


def test_malformed_signature_bits_are_rejected() -> None:
    signed = sign_message()
    response = client.post(
        "/api/security/check",
        json=transaction_payload(signed, signature_bits="not-binary"),
    )
    assert response.status_code == 422
