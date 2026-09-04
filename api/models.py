"""Validated API request and response models for Q-Sign Shield V0.6."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Reject unknown fields and normalize surrounding string whitespace."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RootResponse(StrictModel):
    project: Literal["Q-Sign Shield"]
    version: Literal["0.6"]
    status: Literal["running"]


class HealthResponse(StrictModel):
    status: Literal["healthy"]


class SignRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4096)
    sender: str = Field(min_length=1, max_length=64)


class SignResponse(StrictModel):
    status: Literal["SIGNED"]
    sender: str
    message: str
    signature_id: str
    message_hash: str
    signature_owner: str
    signature_fingerprint: str
    total_bits: int


class VerifyRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4096)
    claimed_sender: str = Field(min_length=1, max_length=64)
    signature_id: str = Field(min_length=1, max_length=64)
    signature_bits: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
        pattern=r"^[01]+$",
        description="Optional presented signature bits for tampering checks.",
    )


class VerifyResponse(StrictModel):
    verification: Literal["PASS", "FAIL"]
    security_decision: str
    cryptographic_signature: Literal["PASS", "FAIL"]
    matching_bits: int
    total_bits: int
    mismatching_bits: int
    verification_percentage: float
    identity_match: bool
    transaction_id: str


class SecurityCheckRequest(VerifyRequest):
    """A transaction presented to the stateful multi-attack detector."""


class SecurityCheckResponse(StrictModel):
    status: Literal["ACCEPTED", "BLOCKED"]
    attack_detected: bool
    attack_type: str | None
    security_decision: str
    cryptographic_signature: Literal["PASS", "FAIL"]
    identity_match: bool
    overall_verification: Literal["PASS", "FAIL"]
    matching_bits: int
    total_bits: int
    mismatching_bits: int
    verification_percentage: float
    sender_identity: str
    signature_owner: str
    transaction_id: str


QuantumScenario = Literal[
    "normal",
    "bit_flip",
    "phase_flip",
    "bit_phase_flip",
    "intercept_resend",
    "channel_noise",
]


class QuantumStatusResponse(StrictModel):
    module: Literal["Quantum Threat Forensics"]
    status: Literal["ready"]
    supported_scenarios: list[QuantumScenario]


class QuantumAnalyzeRequest(StrictModel):
    scenario: QuantumScenario
    shots: int = Field(default=1024, ge=128, le=8192, strict=True)


class QuantumMeasurementsResponse(StrictModel):
    z_basis_counts: dict[str, int]
    x_basis_counts: dict[str, int]
    z_basis_error_rate: float
    x_basis_error_rate: float
    z_basis_correlation_rate: float
    x_basis_correlation_rate: float
    qber: float
    correlation_rate: float
    matching_measurements: int
    mismatching_measurements: int
    total_measurements: int
    z_matching_measurements: int
    z_mismatching_measurements: int
    x_matching_measurements: int
    x_mismatching_measurements: int
    measurement_fidelity: float
    bell_correlation_score: float


class QuantumForensicsResponse(StrictModel):
    channel_status: Literal["SECURE", "DEGRADED", "COMPROMISED"]
    attack_detected: bool
    anomaly_detected: bool
    probable_attack: Literal[
        "BIT_FLIP",
        "PHASE_FLIP",
        "BIT_PHASE_FLIP",
        "INTERCEPT_RESEND",
        "CHANNEL_NOISE",
    ] | None
    qber: float
    z_basis_error_rate: float
    x_basis_error_rate: float
    correlation_rate: float
    measurement_fidelity: float
    bell_correlation_score: float
    pauli_anomalies: dict[str, float]
    dominant_pauli_syndrome: Literal["NONE", "X", "Y", "Z"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    classification_reason: str


class QuantumAnalyzeResponse(StrictModel):
    scenario: QuantumScenario
    shots: int
    measurements: QuantumMeasurementsResponse
    forensics: QuantumForensicsResponse
    detection_correct: bool
