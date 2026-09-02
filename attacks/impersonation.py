"""Signer-identity impersonation simulation for Q-Sign Shield V0.5."""

from __future__ import annotations

from typing import Any


def simulate_impersonation_attempt(
    claimed_sender: str,
    original_signature: dict[str, Any],
) -> dict[str, Any]:
    """Reuse a real signer's signature while claiming a different identity."""
    signature_owner = original_signature.get("signer")
    if not isinstance(signature_owner, str) or not signature_owner:
        raise ValueError("The signature does not contain a valid owner identity.")
    if claimed_sender == signature_owner:
        raise ValueError("An impersonation identity must differ from the signature owner.")

    return {
        "attack_type": "IMPERSONATION_ATTEMPT",
        "claimed_sender": claimed_sender,
        "signature_owner": signature_owner,
        "signature_id": original_signature.get("signature_id"),
        "attacker_action": "Claiming another identity while reusing its signature",
        "reused_signature": original_signature,
    }
