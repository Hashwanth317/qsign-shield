"""Bell-pair quantum-channel experiments for Q-Sign Shield V0.8."""

from __future__ import annotations

from typing import Any, Literal, cast

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator

from attacks.quantum_channel import (
    QuantumChannelScenario,
    apply_quantum_channel_attack,
    build_channel_noise_model,
    normalize_scenario,
)
from quantum.measurements import (
    calculate_channel_metrics,
    canonicalize_two_qubit_counts,
)
from security.config import (
    DEFAULT_CHANNEL_SHOTS,
    DEFAULT_SIMULATOR_SEED,
    MAX_CHANNEL_SHOTS,
    MIN_CHANNEL_SHOTS,
)


MeasurementBasis = Literal["z", "x"]


def _validate_basis(basis: str) -> MeasurementBasis:
    normalized = basis.strip().lower()
    if normalized not in {"z", "x"}:
        raise ValueError("Measurement basis must be 'z' or 'x'.")
    return cast(MeasurementBasis, normalized)


def _validate_shots(shots: int) -> None:
    if isinstance(shots, bool) or not isinstance(shots, int):
        raise TypeError("shots must be an integer.")
    if not MIN_CHANNEL_SHOTS <= shots <= MAX_CHANNEL_SHOTS:
        raise ValueError(
            f"shots must be between {MIN_CHANNEL_SHOTS} and "
            f"{MAX_CHANNEL_SHOTS}."
        )


def build_bell_channel_circuit(
    scenario: str = "normal",
    basis: str = "z",
) -> QuantumCircuit:
    """Build a |Phi+> channel and apply one controlled simulator scenario."""
    normalized_scenario = normalize_scenario(scenario)
    normalized_basis = _validate_basis(basis)

    qubits = QuantumRegister(2, "q")
    outcomes = ClassicalRegister(2, "outcome")

    if normalized_scenario == "intercept_resend":
        eve = ClassicalRegister(1, "eve")
        circuit = QuantumCircuit(qubits, outcomes, eve)
        eve_measurement = eve[0]
    else:
        circuit = QuantumCircuit(qubits, outcomes)
        eve_measurement = None

    # Bell-pair reference: |Phi+> = (|00> + |11>) / sqrt(2).
    circuit.h(qubits[0])
    circuit.cx(qubits[0], qubits[1])
    circuit.barrier()

    apply_quantum_channel_attack(
        circuit,
        qubits[1],
        normalized_scenario,
        eve_measurement=eve_measurement,
    )
    circuit.barrier()

    # H rotates the X eigenbasis onto the computational measurement basis.
    if normalized_basis == "x":
        circuit.h(qubits[0])
        circuit.h(qubits[1])

    circuit.measure(qubits[0], outcomes[0])
    circuit.measure(qubits[1], outcomes[1])
    return circuit


def run_basis_experiment(
    scenario: str = "normal",
    basis: str = "z",
    shots: int = DEFAULT_CHANNEL_SHOTS,
    seed: int = DEFAULT_SIMULATOR_SEED,
) -> dict[str, Any]:
    """Execute one basis check and return canonical two-qubit counts."""
    normalized_scenario = normalize_scenario(scenario)
    normalized_basis = _validate_basis(basis)
    _validate_shots(shots)

    circuit = build_bell_channel_circuit(normalized_scenario, normalized_basis)
    noise_model = (
        build_channel_noise_model()
        if normalized_scenario == "channel_noise"
        else None
    )
    simulator = AerSimulator(noise_model=noise_model)
    compiled = transpile(
        circuit,
        simulator,
        optimization_level=0,
        seed_transpiler=seed,
    )
    result = simulator.run(
        compiled,
        shots=shots,
        seed_simulator=seed,
    ).result()
    counts = canonicalize_two_qubit_counts(result.get_counts(compiled))
    return {
        "basis": normalized_basis,
        "shots": shots,
        "counts": counts,
        "circuit": circuit,
    }


def run_quantum_channel_experiment(
    scenario: str = "normal",
    shots: int = DEFAULT_CHANNEL_SHOTS,
    seed: int = DEFAULT_SIMULATOR_SEED,
) -> dict[str, Any]:
    """Run independent Z/X checks and calculate observed channel metrics."""
    normalized_scenario = normalize_scenario(scenario)
    _validate_shots(shots)
    z_result = run_basis_experiment(normalized_scenario, "z", shots, seed)
    x_result = run_basis_experiment(normalized_scenario, "x", shots, seed + 1)
    measurements = calculate_channel_metrics(
        z_result["counts"],
        x_result["counts"],
    )
    return {
        "scenario": normalized_scenario,
        "shots": shots,
        "measurements": measurements,
    }
