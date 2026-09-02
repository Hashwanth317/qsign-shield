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
