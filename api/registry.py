"""Process-local signature storage for the V0.6 prototype API."""

from __future__ import annotations

from typing import Any


class SignatureRegistry:
    """Store generated signature objects by ID until the API process exits."""

    def __init__(self) -> None:
        self._signatures: dict[str, dict[str, Any]] = {}

    def store(self, signature: dict[str, Any]) -> None:
        signature_id = signature.get("signature_id")
        if not isinstance(signature_id, str) or not signature_id:
            raise ValueError("A generated signature must contain a signature ID.")
        self._signatures[signature_id] = signature

    def get(self, signature_id: str) -> dict[str, Any] | None:
        return self._signatures.get(signature_id)

    def clear(self) -> None:
        """Clear in-memory state, primarily for tests and local development."""
        self._signatures.clear()
