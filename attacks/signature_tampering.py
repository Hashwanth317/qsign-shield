"""Deterministic signature-tampering simulation for Q-Sign Shield V0.5."""

from __future__ import annotations

from typing import Any, Iterable


def simulate_signature_tampering(
    original_signature: dict[str, Any],
    bit_positions: Iterable[int] = (0, 1),
) -> dict[str, Any]:
    """Return a copied signature with selected received bits flipped.

    Positions are zero-based. The original signature object is never modified.
    This is an educational, deterministic attack simulation.
    """
    original_bits = original_signature.get("received_signature_bits")
    if not isinstance(original_bits, str) or not original_bits:
        raise ValueError("The signature has no received signature bits to tamper with.")

    positions = tuple(dict.fromkeys(bit_positions))
    if not positions:
        raise ValueError("At least one bit position must be supplied.")
    if any(not isinstance(position, int) for position in positions):
        raise ValueError("Every tampering position must be an integer.")
    if any(position < 0 or position >= len(original_bits) for position in positions):
        raise ValueError("A tampering position is outside the signature bit range.")

    tampered_bits = list(original_bits)
    for position in positions:
        bit = tampered_bits[position]
        if bit not in {"0", "1"}:
            raise ValueError("Signature bits must contain only 0 and 1.")
        tampered_bits[position] = "1" if bit == "0" else "0"

    tampered_signature = original_signature.copy()
    tampered_signature["received_signature_bits"] = "".join(tampered_bits)

    return {
        "attack_type": "SIGNATURE_TAMPERING",
        "signature_id": original_signature.get("signature_id"),
        "tampered_positions": positions,
        "original_signature_bits": original_bits,
        "tampered_signature_bits": tampered_signature["received_signature_bits"],
        "attacker_action": "Flipping received quantum-signature bits",
        "tampered_signature": tampered_signature,
    }
