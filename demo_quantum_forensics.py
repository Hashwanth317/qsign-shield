"""Terminal demonstration of Q-Sign Shield V0.8 channel forensics."""

from attacks.quantum_channel import SUPPORTED_QUANTUM_SCENARIOS
from quantum.channel import run_quantum_channel_experiment
from security.config import DEFAULT_CHANNEL_SHOTS
from security.quantum_forensics import analyze_quantum_forensics


SCENARIO_TITLES = {
    "normal": "NORMAL CHANNEL",
    "bit_flip": "BIT-FLIP ATTACK",
    "phase_flip": "PHASE-FLIP ATTACK",
    "bit_phase_flip": "BIT + PHASE FLIP",
    "intercept_resend": "INTERCEPT-RESEND",
    "channel_noise": "CHANNEL NOISE",
}


def detection_is_correct(scenario: str, probable_attack: str | None) -> bool:
    """Compare ground truth only after statistics-only classification."""
    if scenario == "normal":
        return probable_attack is None
    return probable_attack == scenario.upper()


def main() -> None:
    """Run all controlled scenarios and print concise observed evidence."""
    print("=" * 52)
    print("                 Q-SIGN SHIELD V0.8")
    print("        QUANTUM CHANNEL THREAT FORENSICS")
    print("=" * 52)

    for index, scenario in enumerate(SUPPORTED_QUANTUM_SCENARIOS, start=1):
        experiment = run_quantum_channel_experiment(
            scenario=scenario,
            shots=DEFAULT_CHANNEL_SHOTS,
        )
        measurements = experiment["measurements"]
        forensics = analyze_quantum_forensics(measurements)
        probable = forensics["probable_attack"] or "NORMAL"
        correct = detection_is_correct(scenario, forensics["probable_attack"])

        print(f"\n[{index}] {SCENARIO_TITLES[scenario]}\n")
        print(f"Shots per basis: {experiment['shots']}")
        print(f"Z-Basis Error: {measurements['z_basis_error_rate']:.2f}%")
        print(f"X-Basis Error: {measurements['x_basis_error_rate']:.2f}%")
        print(f"Combined Correlation: {measurements['correlation_rate']:.2f}%")
        print(f"QBER: {measurements['qber']:.2f}%")
        print(
            "Measurement Fidelity: "
            f"{measurements['measurement_fidelity']:.2f}%"
        )
        print(
            "Pauli Syndrome: "
            f"{forensics['dominant_pauli_syndrome']}"
        )
        print(f"Simulated Scenario: {scenario.upper()}")
        print(f"Forensics Prediction: {probable}")
        print(f"Detection Correct: {str(correct).lower()}")
        print(f"Channel Status: {forensics['channel_status']}")
        print(f"Risk Level: {forensics['risk_level']}")

        if index != len(SUPPORTED_QUANTUM_SCENARIOS):
            print("\n" + "-" * 52)

    print("\n" + "=" * 52)
    print("Educational Qiskit Aer simulation — not physical QKD hardware.")
    print("=" * 52)


if __name__ == "__main__":
    main()

