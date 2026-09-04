"""Shot-based measurement statistics for Bell-pair security checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


CORRELATED_OUTCOMES = frozenset({"00", "11"})
MISMATCHED_OUTCOMES = frozenset({"01", "10"})


def canonicalize_two_qubit_counts(counts: Mapping[str, int]) -> dict[str, int]:
    """Return counts for the final two-bit output register.

    Intercept-resend circuits also contain Eve's classical bit. Qiskit prints
    separate classical registers with spaces, so the final output register is
    selected without treating Eve's private result as a channel outcome.
    """
    canonical = {outcome: 0 for outcome in ("00", "01", "10", "11")}
    for raw_outcome, count in counts.items():
        output_register = raw_outcome.split()[-1]
        if output_register not in canonical:
            raise ValueError(f"Unexpected two-qubit outcome: {raw_outcome!r}.")
        canonical[output_register] += int(count)
    return canonical


def summarize_basis_counts(counts: Mapping[str, int]) -> dict[str, Any]:
    """Calculate correlation and mismatch statistics for one basis."""
    canonical = canonicalize_two_qubit_counts(counts)
    total = sum(canonical.values())
    if total <= 0:
        raise ValueError("Measurement counts must contain at least one shot.")

    matching = sum(canonical[outcome] for outcome in CORRELATED_OUTCOMES)
    mismatching = sum(canonical[outcome] for outcome in MISMATCHED_OUTCOMES)
    return {
        "counts": canonical,
        "matching_measurements": matching,
        "mismatching_measurements": mismatching,
        "total_measurements": total,
        "error_rate": (mismatching / total) * 100.0,
        "correlation_rate": (matching / total) * 100.0,
    }


def calculate_channel_metrics(
    z_basis_counts: Mapping[str, int],
    x_basis_counts: Mapping[str, int],
) -> dict[str, Any]:
    """Combine Z- and X-basis observations into transparent metrics.

    QBER is the percentage of mismatched outcomes across both basis checks.
    For the ideal |Phi+> Bell reference, 00 and 11 are matches in either basis.
    ``measurement_fidelity`` is the same observed agreement percentage and is
    deliberately not presented as quantum-state fidelity. The normalized Bell
    correlation score is simply measurement_fidelity divided by 100.
    """
    z_summary = summarize_basis_counts(z_basis_counts)
    x_summary = summarize_basis_counts(x_basis_counts)

    matching = (
        z_summary["matching_measurements"]
        + x_summary["matching_measurements"]
    )
    mismatching = (
        z_summary["mismatching_measurements"]
        + x_summary["mismatching_measurements"]
    )
    total = z_summary["total_measurements"] + x_summary["total_measurements"]
    qber = (mismatching / total) * 100.0
    correlation_rate = (matching / total) * 100.0

    return {
        "z_basis_counts": z_summary["counts"],
        "x_basis_counts": x_summary["counts"],
        "z_basis_error_rate": z_summary["error_rate"],
        "x_basis_error_rate": x_summary["error_rate"],
        "z_basis_correlation_rate": z_summary["correlation_rate"],
        "x_basis_correlation_rate": x_summary["correlation_rate"],
        "qber": qber,
        "correlation_rate": correlation_rate,
        "matching_measurements": matching,
        "mismatching_measurements": mismatching,
        "total_measurements": total,
        "z_matching_measurements": z_summary["matching_measurements"],
        "z_mismatching_measurements": z_summary["mismatching_measurements"],
        "x_matching_measurements": x_summary["matching_measurements"],
        "x_mismatching_measurements": x_summary["mismatching_measurements"],
        "measurement_fidelity": correlation_rate,
        "bell_correlation_score": correlation_rate / 100.0,
    }

