"""Educational Quantum Digital Signature (QDS) simulation helpers.

This module links signer identity to message fingerprint bits and sends the
result through the existing teleportation simulation. It is not a complete
or production-ready QDS cryptographic construction.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any
from uuid import uuid4

from quantum.encoder import encode_message
from quantum.teleportation import run_teleportation


# Simulation-only signer parameters: public deterministic masks, not secrets.
SIGNER_KEYS = {
    "Alice": "10101100111100010110100101011010",
    "Bob": "01010011000011101001011010100101",
    "Charlie": "11000011101001010011110001101001",
}

# This identity remains reserved for the impersonation demonstration and
# cannot own a generated signature through the public signing API.
RESERVED_SIGNERS = frozenset({"attacker"})


def _validate_signer(signer: str) -> str:
    """Return a stable simulation mask for a legitimate signer identity."""
    normalized = signer.strip()
    if not normalized or normalized.casefold() in RESERVED_SIGNERS:
        raise ValueError(
            f"Unknown signer {signer!r}. The identity cannot generate a signature."
        )

    if normalized in SIGNER_KEYS:
        return SIGNER_KEYS[normalized]

    # Dynamic identities use a repeatable, public SHA-256-derived mask so the
    # existing verifier can reproduce it. This remains an educational identity
    # binding and is not a secret key or production QDS construction.
    identity_digest = sha256(
        f"Q-SIGN-SHIELD-SIMULATED-SIGNER:{normalized.casefold()}".encode("utf-8")
    ).digest()
    return "".join(f"{byte:08b}" for byte in identity_digest)


def _apply_signer_mask(message_bits: str, mask: str) -> tuple[str, str]:
    """XOR message bits with a repeated signer mask for this simulation."""
    selected_mask = "".join(mask[index % len(mask)] for index in range(len(message_bits)))

    # XOR only associates signer identity with these demo signature bits. It is
    # not intended to represent a real-world QDS signing construction.
    signature_bits = "".join(
        str(int(message_bit) ^ int(mask_bit))
        for message_bit, mask_bit in zip(message_bits, selected_mask)
    )
    return selected_mask, signature_bits


def _bit_mismatches(expected: str, received: str) -> int:
    """Count differing bits, including missing or additional bits."""
    shared = sum(a != b for a, b in zip(expected, received))
    return shared + abs(len(expected) - len(received))


def generate_quantum_signature(
    signer: str,
    message: str,
    sample_bits: int = 16,
    shots: int = 256,
) -> dict[str, Any]:
    """Generate signer-linked bits and teleport them to Bob one at a time."""
    signer_mask = _validate_signer(signer)
    if not 1 <= sample_bits <= 256:
        raise ValueError("sample_bits must be between 1 and 256.")
    if shots <= 0:
        raise ValueError("shots must be a positive integer.")

    encoded = encode_message(message, sample_bits=sample_bits)
    selected_mask, expected_bits = _apply_signer_mask(
        encoded["selected_bits"], signer_mask
    )
    received_bits: list[str] = []
    transmissions: list[dict[str, Any]] = []
    success_rates: list[float] = []

    for index, expected_bit in enumerate(expected_bits, start=1):
        result = run_teleportation(secret_bit=int(expected_bit), shots=shots)
        received_bit = str(result["received_bit"])
        received_bits.append(received_bit)
        success_rates.append(result["success_rate"])
        transmissions.append({
            "position": index,
            "expected_bit": int(expected_bit),
            "received_bit": result["received_bit"],
            "success_rate": result["success_rate"],
        })

    received_signature = "".join(received_bits)
    mismatches = _bit_mismatches(expected_bits, received_signature)
    total_bits = len(expected_bits)
    return {
        "signature_id": f"QS-{uuid4().hex[:8].upper()}",
        "signer": signer,
        "message": message,
        "message_hash": encoded["hash"],
        "message_bits": encoded["selected_bits"],
        "signer_mask": selected_mask,
        "expected_signature_bits": expected_bits,
        "received_signature_bits": received_signature,
        "total_bits": total_bits,
        "correctly_received_bits": total_bits - mismatches,
        "mismatches": mismatches,
        "mismatch_rate": mismatches / total_bits,
        "average_teleportation_success": sum(success_rates) / total_bits,
        "transmissions": transmissions,
    }


def verify_quantum_signature(
    signer: str,
    message: str,
    signature: dict[str, Any],
    threshold: float = 0.05,
) -> dict[str, Any]:
    """Independently verify message integrity, signer, and received QDS bits."""
    signer_mask = _validate_signer(signer)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0.0 and 1.0.")
    total_bits = signature.get("total_bits", 0)
    if not isinstance(total_bits, int) or not 1 <= total_bits <= 256:
        raise ValueError("Signature contains an invalid total_bits value.")

    encoded = encode_message(message, sample_bits=total_bits)
    _, expected_bits = _apply_signer_mask(encoded["selected_bits"], signer_mask)
    received_bits = signature.get("received_signature_bits", "")
    if not isinstance(received_bits, str):
        raise ValueError("Signature contains invalid received signature bits.")

    mismatches = _bit_mismatches(expected_bits, received_bits)
    mismatch_rate = mismatches / total_bits
    message_integrity = encoded["hash"] == signature.get("message_hash")
    signer_valid = signer == signature.get("signer") and mismatch_rate <= threshold

    # This is a configurable simulation threshold, not a scientifically proven
    # security threshold. It must be calibrated experimentally in later work.
    quantum_signature_match = mismatch_rate <= threshold
    decision = "VALID" if (
        message_integrity and signer_valid and quantum_signature_match
    ) else "INVALID"
    return {
        "signature_id": signature.get("signature_id"),
        "claimed_signer": signer,
        "message_integrity": message_integrity,
        "signer_valid": signer_valid,
        "quantum_signature_match": quantum_signature_match,
        "mismatch_count": mismatches,
        "mismatch_rate": mismatch_rate,
        "threshold": threshold,
        "decision": decision,
    }
