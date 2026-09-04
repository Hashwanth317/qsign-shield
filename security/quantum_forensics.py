"""Statistics-only quantum-channel forensics for Q-Sign Shield V0.8."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from security.config import (
    CORRELATION_MINIMUM,
    FIDELITY_MINIMUM,
    INTERCEPT_RESEND_ERROR_MAXIMUM,
    INTERCEPT_RESEND_ERROR_MINIMUM,
    INTERCEPT_RESEND_PRESERVED_BASIS_MAXIMUM,
    PAULI_CLEAN_BASIS_MAXIMUM,
    PAULI_STRONG_ERROR_MINIMUM,
    QBER_ATTACK_THRESHOLD,
    QBER_WARNING_THRESHOLD,
)


def infer_pauli_disturbance(
    z_basis_error_rate: float,
    x_basis_error_rate: float,
) -> dict[str, Any]:
    """Infer Pauli-like syndrome evidence from complementary-basis errors.

    X errors break Z-basis Bell correlation, Z errors break X-basis
    correlation, and Y-like evidence is the error shared by both. The scores
    are normalized observations, not physical error-channel tomography.
    """
    z_observed = max(0.0, min(float(z_basis_error_rate) / 100.0, 1.0))
    x_observed = max(0.0, min(float(x_basis_error_rate) / 100.0, 1.0))
    scores = {
        "x_anomaly": max(z_observed - x_observed, 0.0),
        "y_anomaly": min(z_observed, x_observed),
        "z_anomaly": max(x_observed - z_observed, 0.0),
    }
    labels = {
        "x_anomaly": "X",
        "y_anomaly": "Y",
        "z_anomaly": "Z",
    }
    strongest_key = max(scores, key=lambda name: scores[name])
    strongest_score = scores[strongest_key]
    dominant = (
        labels[strongest_key]
        if strongest_score > QBER_WARNING_THRESHOLD / 100.0
        else "NONE"
    )
    return {
        **{name: round(value, 4) for name, value in scores.items()},
        "dominant_syndrome": dominant,
    }


def _required_percentage(measurements: Mapping[str, Any], key: str) -> float:
    try:
        value = float(measurements[key])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Observed measurements require numeric {key!r}.") from error
    if not 0.0 <= value <= 100.0:
        raise ValueError(f"Observed {key!r} must be between 0 and 100.")
    return value


def analyze_quantum_forensics(measurements: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a channel using only observed metrics, never scenario labels."""
    z_error = _required_percentage(measurements, "z_basis_error_rate")
    x_error = _required_percentage(measurements, "x_basis_error_rate")
    qber = _required_percentage(measurements, "qber")
    correlation = _required_percentage(measurements, "correlation_rate")
    fidelity = _required_percentage(measurements, "measurement_fidelity")
    syndrome = infer_pauli_disturbance(z_error, x_error)

    normal = (
        z_error <= QBER_WARNING_THRESHOLD
        and x_error <= QBER_WARNING_THRESHOLD
        and correlation >= CORRELATION_MINIMUM
        and fidelity >= FIDELITY_MINIMUM
    )
    strong_z_disturbance = z_error >= PAULI_STRONG_ERROR_MINIMUM
    strong_x_disturbance = x_error >= PAULI_STRONG_ERROR_MINIMUM
    clean_z_basis = z_error <= PAULI_CLEAN_BASIS_MAXIMUM
    clean_x_basis = x_error <= PAULI_CLEAN_BASIS_MAXIMUM
    intercept_pattern = (
        z_error <= INTERCEPT_RESEND_PRESERVED_BASIS_MAXIMUM
        and INTERCEPT_RESEND_ERROR_MINIMUM
        <= x_error
        <= INTERCEPT_RESEND_ERROR_MAXIMUM
    )

    if normal:
        probable_attack = None
        channel_status = "SECURE"
        risk_level = "LOW"
        reason = "Both complementary-basis checks retain Bell correlation."
    elif strong_z_disturbance and clean_x_basis:
        probable_attack = "BIT_FLIP"
        channel_status = "COMPROMISED"
        risk_level = "HIGH"
        reason = "Z correlation failed while X correlation remained stable."
    elif strong_x_disturbance and clean_z_basis:
        probable_attack = "PHASE_FLIP"
        channel_status = "COMPROMISED"
        risk_level = "HIGH"
        reason = "X correlation failed while Z correlation remained stable."
    elif strong_z_disturbance and strong_x_disturbance:
        probable_attack = "BIT_PHASE_FLIP"
        channel_status = "COMPROMISED"
        risk_level = "HIGH"
        reason = "Both complementary-basis correlations failed strongly."
    elif intercept_pattern:
        probable_attack = "INTERCEPT_RESEND"
        channel_status = "COMPROMISED"
        risk_level = "HIGH"
        reason = (
            "Z correlation was preserved but X coherence fell to a random-like "
            "level consistent with Z-basis intercept/resend."
        )
    else:
        probable_attack = "CHANNEL_NOISE"
        severe_degradation = qber >= QBER_ATTACK_THRESHOLD
        channel_status = "COMPROMISED" if severe_degradation else "DEGRADED"
        risk_level = "HIGH" if severe_degradation else "MEDIUM"
        reason = "Moderate or diffuse errors do not match a strong Pauli pattern."

    # Natural noise is an anomaly but is not labelled as an intentional attack.
    attack_detected = probable_attack not in {None, "CHANNEL_NOISE"}
    return {
        "channel_status": channel_status,
        "attack_detected": attack_detected,
        "anomaly_detected": probable_attack is not None,
        "probable_attack": probable_attack,
        "qber": qber,
        "z_basis_error_rate": z_error,
        "x_basis_error_rate": x_error,
        "correlation_rate": correlation,
        "measurement_fidelity": fidelity,
        "bell_correlation_score": float(
            measurements.get("bell_correlation_score", fidelity / 100.0)
        ),
        "pauli_anomalies": {
            "x_anomaly": syndrome["x_anomaly"],
            "y_anomaly": syndrome["y_anomaly"],
            "z_anomaly": syndrome["z_anomaly"],
        },
        "dominant_pauli_syndrome": syndrome["dominant_syndrome"],
        "risk_level": risk_level,
        "classification_reason": reason,
    }
