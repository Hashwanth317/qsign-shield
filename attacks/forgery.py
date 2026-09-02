"""Message-forgery simulation for the Q-Sign Shield prototype.

The attacker changes the message and reuses an existing signature. No new
signature is generated here.
"""

from __future__ import annotations

from typing import Any

from quantum.encoder import hash_message


def simulate_forgery_attack(
    original_message: str,
    forged_message: str,
    original_signature: dict[str, Any],
) -> dict[str, Any]:
    """Build an attack record that pairs a changed message with an old signature."""
    if original_message == forged_message:
        raise ValueError("The forged message must differ from the original message.")

    signed_message = original_signature.get("message")
    if signed_message is not None and signed_message != original_message:
        raise ValueError("The supplied signature does not belong to the original message.")

    return {
        "attack_type": "MESSAGE_SIGNATURE_FORGERY",
        "original_message": original_message,
        "forged_message": forged_message,
        "original_message_hash": hash_message(original_message),
        "forged_message_hash": hash_message(forged_message),
        "signature_id": original_signature.get("signature_id"),
        "attacker_action": "Reusing original quantum signature",
        # Reuse the same object: the attacker does not generate or alter a signature.
        "reused_signature": original_signature,
    }
