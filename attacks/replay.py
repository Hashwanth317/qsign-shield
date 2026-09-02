"""Replay-attack input preparation for Q-Sign Shield V0.5."""

from __future__ import annotations

from typing import Any


def simulate_replay_attack(
    message: str,
    signature: dict[str, Any],
) -> dict[str, Any]:
    """Return two submissions containing the exact same message and signature."""
    submission = {"message": message, "signature": signature}
    return {
        "attack_type": "REPLAY_ATTACK",
        "signature_id": signature.get("signature_id"),
        "first_submission": submission,
        # The signature is deliberately reused; no signing operation occurs.
        "replayed_submission": submission.copy(),
        "attacker_action": "Resubmitting the same transaction and signature",
    }
