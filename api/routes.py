"""REST routes wrapping the existing Q-Sign Shield V0.1-V0.5 engine."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth import get_current_user, require_security_operator
from api.models import (
    QuantumAnalyzeRequest,
    QuantumAnalyzeResponse,
    QuantumStatusResponse,
    SecurityCheckRequest,
    SecurityCheckResponse,
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse,
)
from attacks.quantum_channel import SUPPORTED_QUANTUM_SCENARIOS
from api.registry import SignatureRegistry
from api.user_models import User
from quantum.channel import run_quantum_channel_experiment
from quantum.qds import generate_quantum_signature
from security.detector import detect_security_event
from security.quantum_forensics import analyze_quantum_forensics
from security.replay_guard import ReplayGuard


router = APIRouter(prefix="/api", tags=["Quantum signature security"])
signature_registry = SignatureRegistry()
replay_guard = ReplayGuard()

ATTACK_TYPE_LABELS = {
    "MESSAGE_FORGERY": "FORGERY",
    "SIGNATURE_TAMPERING": "SIGNATURE_TAMPERING",
    "REPLAY_ATTACK": "REPLAY",
    "IMPERSONATION_ATTEMPT": "IMPERSONATION",
}


def reset_api_state() -> None:
    """Reset prototype-only memory state for isolated automated tests."""
    signature_registry.clear()
    replay_guard.clear()


def _get_signature(signature_id: str) -> dict[str, Any]:
    signature = signature_registry.get(signature_id)
    if signature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signature ID {signature_id!r} was not found.",
        )
    return signature


def _presented_signature(
    stored_signature: dict[str, Any],
    signature_bits: str | None,
) -> dict[str, Any]:
    """Use stored data unless the client presents potentially altered bits."""
    if signature_bits is None:
        return stored_signature
    presented = stored_signature.copy()
    presented["received_signature_bits"] = signature_bits
    return presented


def _detect(
    request: VerifyRequest,
    *,
    use_replay_guard: bool,
) -> dict[str, Any]:
    stored_signature = _get_signature(request.signature_id)
    signature = _presented_signature(stored_signature, request.signature_bits)
    try:
        return detect_security_event(
            sender_identity=request.claimed_sender,
            message=request.message,
            signature=signature,
            replay_guard=replay_guard if use_replay_guard else None,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The supplied transaction could not be verified: {error}",
        ) from error


@router.post(
    "/sign",
    response_model=SignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a simulated quantum signature",
    description=(
        "Generate a 16-bit educational QDS signature with the existing quantum "
        "teleportation workflow and store it in process memory."
    ),
)
def sign_message(
    request: SignRequest,
    _: User = Depends(get_current_user),
) -> SignResponse:
    try:
        signature = generate_quantum_signature(
            signer=request.sender,
            message=request.message,
            sample_bits=16,
            shots=256,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    signature_registry.store(signature)
    return SignResponse(
        status="SIGNED",
        sender=request.sender,
        message=request.message,
        signature_id=signature["signature_id"],
        message_hash=f"{signature['message_hash'][:16]}...",
        signature_owner=signature["signer"],
        signature_fingerprint=signature["received_signature_bits"],
        total_bits=signature["total_bits"],
    )


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify a stored signed transaction",
    description=(
        "Verify a message and claimed sender against a stored signature without "
        "recording the request in replay history."
    ),
)
def verify_message(
    request: VerifyRequest,
    _: User = Depends(get_current_user),
) -> VerifyResponse:
    result = _detect(request, use_replay_guard=False)
    return VerifyResponse(
        verification=result["overall_verification"],
        security_decision=result["security_decision"],
        cryptographic_signature=result["cryptographic_signature"],
        matching_bits=result["matching_signature_bits"],
        total_bits=result["total_signature_bits"],
        mismatching_bits=result["mismatching_signature_bits"],
        verification_percentage=result["verification_percentage"],
        identity_match=result["identity_match"],
        transaction_id=result["transaction_id"],
    )


@router.post(
    "/security/check",
    response_model=SecurityCheckResponse,
    summary="Run multi-attack security verification",
    description=(
        "Run the existing V0.5 detector and process-local replay guard. The "
        "server infers the attack type from message, signature, identity, and "
        "submission history rather than trusting an attack label."
    ),
)
def check_security(
    request: SecurityCheckRequest,
    _: User = Depends(require_security_operator),
) -> SecurityCheckResponse:
    result = _detect(request, use_replay_guard=True)
    attack_detected = result["attack_type"] != "NONE"
    return SecurityCheckResponse(
        status="BLOCKED" if attack_detected else "ACCEPTED",
        attack_detected=attack_detected,
        attack_type=ATTACK_TYPE_LABELS.get(result["attack_type"]),
        security_decision=result["security_decision"],
        cryptographic_signature=result["cryptographic_signature"],
        identity_match=result["identity_match"],
        overall_verification=result["overall_verification"],
        matching_bits=result["matching_signature_bits"],
        total_bits=result["total_signature_bits"],
        mismatching_bits=result["mismatching_signature_bits"],
        verification_percentage=result["verification_percentage"],
        sender_identity=result["sender_identity"],
        signature_owner=result["signature_owner_identity"],
        transaction_id=result["transaction_id"],
    )


@router.get(
    "/quantum/status",
    response_model=QuantumStatusResponse,
    tags=["Quantum threat forensics"],
    summary="Report quantum forensics capability",
)
def quantum_forensics_status(
    _: User = Depends(require_security_operator),
) -> QuantumStatusResponse:
    """Return the simulator scenarios available to V0.8 clients."""
    return QuantumStatusResponse(
        module="Quantum Threat Forensics",
        status="ready",
        supported_scenarios=list(SUPPORTED_QUANTUM_SCENARIOS),
    )


@router.post(
    "/quantum/analyze",
    response_model=QuantumAnalyzeResponse,
    tags=["Quantum threat forensics"],
    summary="Simulate and analyze a Bell-pair channel",
    description=(
        "Run a seeded Qiskit Aer educational scenario, measure independent "
        "Bell pairs in Z and X bases, and classify only the observed statistics."
    ),
)
def analyze_quantum_channel(
    request: QuantumAnalyzeRequest,
    _: User = Depends(require_security_operator),
) -> QuantumAnalyzeResponse:
    """Run the simulator and keep its ground truth outside the classifier."""
    experiment = run_quantum_channel_experiment(
        scenario=request.scenario,
        shots=request.shots,
    )
    forensics = analyze_quantum_forensics(experiment["measurements"])
    predicted = forensics["probable_attack"]
    detection_correct = (
        predicted is None
        if request.scenario == "normal"
        else predicted == request.scenario.upper()
    )
    return QuantumAnalyzeResponse(
        scenario=request.scenario,
        shots=request.shots,
        measurements=experiment["measurements"],
        forensics=forensics,
        detection_correct=detection_correct,
    )
