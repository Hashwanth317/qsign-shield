"""Forgery classification built on the existing V0.3 QDS verifier."""

from __future__ import annotations

from typing import Any

from quantum.qds import verify_quantum_signature
from security.replay_guard import ReplayGuard


def detect_forgery(
    signer: str,
    message: str,
    signature: dict[str, Any],
    threshold: float = 0.05,
) -> dict[str, Any]:
    """Verify a message/signature pair and classify its security outcome."""
    verification = verify_quantum_signature(
        signer=signer,
        message=message,
        signature=signature,
        threshold=threshold,
    )

    total_bits = signature["total_bits"]
    mismatching_bits = verification["mismatch_count"]
    matching_bits = max(total_bits - mismatching_bits, 0)
    verification_percentage = (matching_bits / total_bits) * 100
    verification_passed = verification["decision"] == "VALID"

    return {
        "signature_id": verification["signature_id"],
        "signature_verification": "PASS" if verification_passed else "FAIL",
        "security_decision": (
            "LEGITIMATE" if verification_passed else "FORGERY DETECTED"
        ),
        "matching_signature_bits": matching_bits,
        "mismatching_signature_bits": mismatching_bits,
        "total_signature_bits": total_bits,
        "verification_percentage": verification_percentage,
        # Retain the complete V0.3 result for future JSON/API use.
        "verification": verification,
    }


def detect_security_event(
    sender_identity: str,
    message: str,
    signature: dict[str, Any],
    replay_guard: ReplayGuard | None = None,
    threshold: float = 0.05,
) -> dict[str, Any]:
    """Classify legitimate, forgery, tampering, replay, and impersonation events.

    All cryptographic checks come from the existing V0.3 verifier. This layer
    only combines those results with identity comparison and optional in-memory
    replay history.
    """
    signature_owner = signature.get("signer")
    if not isinstance(signature_owner, str) or not signature_owner:
        raise ValueError("The signature does not contain a valid owner identity.")
    identity_match = sender_identity == signature_owner

    # Cryptographic validity belongs to the signature and its recorded owner.
    # The claimed sender is checked separately as an authorization condition.
    verification = verify_quantum_signature(
        signer=signature_owner,
        message=message,
        signature=signature,
        threshold=threshold,
    )

    total_bits = signature["total_bits"]
    mismatching_bits = verification["mismatch_count"]
    matching_bits = max(total_bits - mismatching_bits, 0)
    verification_percentage = (matching_bits / total_bits) * 100

    attack_type = "NONE"
    decision = "LEGITIMATE"
    submission_status = "ACCEPTED"

    # Classification order keeps the primary cause explicit. Replay history is
    # consulted only after the message, identity, and signature all verify.
    if not identity_match:
        attack_type = "IMPERSONATION_ATTEMPT"
        decision = "IMPERSONATION ATTACK DETECTED"
        submission_status = "REJECTED"
    elif not verification["message_integrity"]:
        attack_type = "MESSAGE_FORGERY"
        decision = "FORGERY ATTACK DETECTED"
        submission_status = "REJECTED"
    elif not verification["quantum_signature_match"]:
        attack_type = "SIGNATURE_TAMPERING"
        decision = "SIGNATURE TAMPERING DETECTED"
        submission_status = "REJECTED"
    elif replay_guard is not None:
        replay_result = replay_guard.check_and_record(signature["signature_id"])
        submission_status = str(replay_result["submission_status"])
        if replay_result["is_replay"]:
            attack_type = "REPLAY_ATTACK"
            decision = "REPLAY ATTACK DETECTED"

    cryptographic_signature_passed = verification["decision"] == "VALID"
    overall_verification_passed = decision == "LEGITIMATE"
    return {
        "attack_type": attack_type,
        "cryptographic_signature": (
            "PASS" if cryptographic_signature_passed else "FAIL"
        ),
        "overall_verification": (
            "PASS" if overall_verification_passed else "FAIL"
        ),
        # Compatibility aliases for existing V0.5 consumers.
        "signature_verification": (
            "PASS" if cryptographic_signature_passed else "FAIL"
        ),
        "verification_result": (
            "PASS" if overall_verification_passed else "FAIL"
        ),
        "matching_signature_bits": matching_bits,
        "mismatching_signature_bits": mismatching_bits,
        "total_signature_bits": total_bits,
        "verification_percentage": verification_percentage,
        "sender_identity": sender_identity,
        "signature_owner_identity": signature_owner,
        "identity_match": identity_match,
        "transaction_id": signature.get("signature_id"),
        "submission_status": submission_status,
        "security_decision": decision,
        "verification": verification,
    }
