"""In-memory replay protection for the educational V0.5 simulation."""

from __future__ import annotations


class ReplayGuard:
    """Track accepted signature IDs for the lifetime of this process only."""

    def __init__(self) -> None:
        self._seen_signature_ids: set[str] = set()

    def check_and_record(self, signature_id: str) -> dict[str, object]:
        """Accept an unseen ID and reject an ID that was already accepted."""
        if not isinstance(signature_id, str) or not signature_id:
            raise ValueError("A non-empty signature ID is required for replay checking.")

        is_replay = signature_id in self._seen_signature_ids
        if not is_replay:
            self._seen_signature_ids.add(signature_id)

        return {
            "signature_id": signature_id,
            "accepted": not is_replay,
            "is_replay": is_replay,
            "submission_status": "REJECTED" if is_replay else "ACCEPTED",
        }

    def clear(self) -> None:
        """Clear process-local history, primarily for demonstrations and tests."""
        self._seen_signature_ids.clear()
