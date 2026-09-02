"""Stable V0.5 multi-attack classification tests."""

import pytest

from attacks.forgery import simulate_forgery_attack
from attacks.impersonation import simulate_impersonation_attempt
from attacks.replay import simulate_replay_attack
from attacks.signature_tampering import simulate_signature_tampering
from quantum.qds import generate_quantum_signature
from security.detector import detect_forgery, detect_security_event
from security.replay_guard import ReplayGuard


SIGNER = "Alice"
ORIGINAL_MESSAGE = "TRANSFER 10000 TO BOB"
FORGED_MESSAGE = "TRANSFER 90000 TO BOB"


@pytest.fixture(scope="module")
def valid_signature() -> dict:
    return generate_quantum_signature(
        SIGNER,
        ORIGINAL_MESSAGE,
        sample_bits=16,
        shots=256,
    )


def test_legitimate_message_passes(valid_signature: dict) -> None:
    result = detect_security_event(SIGNER, ORIGINAL_MESSAGE, valid_signature)
    assert result["cryptographic_signature"] == "PASS"
    assert result["overall_verification"] == "PASS"
    assert result["verification_result"] == "PASS"
    assert result["security_decision"] == "LEGITIMATE"


def test_message_forgery_is_detected(valid_signature: dict) -> None:
    attack = simulate_forgery_attack(
        ORIGINAL_MESSAGE, FORGED_MESSAGE, valid_signature
    )
    result = detect_security_event(
        SIGNER, attack["forged_message"], attack["reused_signature"]
    )
    assert result["attack_type"] == "MESSAGE_FORGERY"
    assert result["security_decision"] == "FORGERY ATTACK DETECTED"


def test_tampered_signature_is_detected(valid_signature: dict) -> None:
    attack = simulate_signature_tampering(valid_signature, bit_positions=(0, 1))
    result = detect_security_event(
        SIGNER, ORIGINAL_MESSAGE, attack["tampered_signature"]
    )
    assert result["mismatching_signature_bits"] >= 2
    assert result["security_decision"] == "SIGNATURE TAMPERING DETECTED"


def test_first_transaction_is_accepted(valid_signature: dict) -> None:
    guard = ReplayGuard()
    result = detect_security_event(
        SIGNER, ORIGINAL_MESSAGE, valid_signature, replay_guard=guard
    )
    assert result["submission_status"] == "ACCEPTED"
    assert result["security_decision"] == "LEGITIMATE"


def test_repeated_transaction_is_detected(valid_signature: dict) -> None:
    replay = simulate_replay_attack(ORIGINAL_MESSAGE, valid_signature)
    guard = ReplayGuard()
    detect_security_event(
        SIGNER,
        replay["first_submission"]["message"],
        replay["first_submission"]["signature"],
        replay_guard=guard,
    )
    repeated = detect_security_event(
        SIGNER,
        replay["replayed_submission"]["message"],
        replay["replayed_submission"]["signature"],
        replay_guard=guard,
    )
    assert repeated["submission_status"] == "REJECTED"
    assert repeated["security_decision"] == "REPLAY ATTACK DETECTED"


def test_matching_identity_passes(valid_signature: dict) -> None:
    result = detect_security_event(SIGNER, ORIGINAL_MESSAGE, valid_signature)
    assert result["identity_match"] is True
    assert result["security_decision"] == "LEGITIMATE"


def test_mismatched_identity_is_impersonation(valid_signature: dict) -> None:
    attack = simulate_impersonation_attempt("Attacker", valid_signature)
    result = detect_security_event(
        attack["claimed_sender"], ORIGINAL_MESSAGE, attack["reused_signature"]
    )
    assert result["cryptographic_signature"] == "PASS"
    assert result["matching_signature_bits"] == 16
    assert result["verification_percentage"] == 100.0
    assert result["identity_match"] is False
    assert result["overall_verification"] == "FAIL"
    assert result["security_decision"] == "IMPERSONATION ATTACK DETECTED"


def test_v04_forgery_detector_still_works(valid_signature: dict) -> None:
    result = detect_forgery(SIGNER, FORGED_MESSAGE, valid_signature)
    assert result["signature_verification"] == "FAIL"
    assert result["security_decision"] == "FORGERY DETECTED"
