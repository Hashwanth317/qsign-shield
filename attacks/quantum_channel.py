"""Educational disturbances applied to a simulated Bell-pair channel."""

from __future__ import annotations

from typing import Literal, cast

from qiskit import QuantumCircuit
from qiskit.circuit import Clbit, Qubit
from qiskit_aer.noise import NoiseModel, pauli_error


QuantumChannelScenario = Literal[
    "normal",
    "bit_flip",
    "phase_flip",
    "bit_phase_flip",
    "intercept_resend",
    "channel_noise",
]

SUPPORTED_QUANTUM_SCENARIOS: tuple[QuantumChannelScenario, ...] = (
    "normal",
    "bit_flip",
    "phase_flip",
    "bit_phase_flip",
    "intercept_resend",
    "channel_noise",
)

# Accidental, symmetric Pauli degradation on the transmitted qubit. X and Y
# disturb Z-basis correlation; Z and Y disturb X-basis correlation.
CHANNEL_NOISE_PROBABILITIES = {
    "I": 0.76,
    "X": 0.08,
    "Y": 0.08,
    "Z": 0.08,
}


def normalize_scenario(scenario: str) -> QuantumChannelScenario:
    """Validate and normalize a public scenario name."""
    normalized = scenario.strip().lower()
    if normalized not in SUPPORTED_QUANTUM_SCENARIOS:
        supported = ", ".join(SUPPORTED_QUANTUM_SCENARIOS)
        raise ValueError(
            f"Unknown quantum-channel scenario {scenario!r}. "
            f"Supported scenarios: {supported}."
        )
    return cast(QuantumChannelScenario, normalized)


def apply_quantum_channel_attack(
    circuit: QuantumCircuit,
    transmitted_qubit: Qubit,
    scenario: QuantumChannelScenario,
    *,
    eve_measurement: Clbit | None = None,
) -> None:
    """Apply the selected simulator disturbance before security measurement.

    Scenario knowledge stops at this simulation boundary. The security
    classifier receives only the resulting measurement statistics.
    """
    if scenario == "normal":
        return
    if scenario == "bit_flip":
        circuit.x(transmitted_qubit)
        return
    if scenario == "phase_flip":
        circuit.z(transmitted_qubit)
        return
    if scenario == "bit_phase_flip":
        # Pauli Y represents an X+Z disturbance up to a global phase.
        circuit.y(transmitted_qubit)
        return
    if scenario == "intercept_resend":
        if eve_measurement is None:
            raise ValueError("Intercept-resend requires an Eve measurement bit.")

        # Eve measures in Z, discards the intercepted state, and prepares a new
        # qubit matching her result. This preserves Z correlation but destroys
        # the phase coherence revealed by an X-basis security check.
        circuit.measure(transmitted_qubit, eve_measurement)
        circuit.reset(transmitted_qubit)
        with circuit.if_test((eve_measurement, True)):
            circuit.x(transmitted_qubit)
        return
    if scenario == "channel_noise":
        # Aer attaches the probabilistic noise model to this explicit channel
        # marker. Keeping it separate avoids affecting clean experiments.
        circuit.id(transmitted_qubit)
        return

    raise ValueError(f"Unsupported quantum-channel scenario: {scenario!r}.")


def build_channel_noise_model() -> NoiseModel:
    """Return the controlled probabilistic Aer model for natural degradation."""
    error = pauli_error(list(CHANNEL_NOISE_PROBABILITIES.items()))
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(error, ["id"])
    return noise_model

