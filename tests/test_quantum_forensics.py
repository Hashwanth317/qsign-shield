"""V0.8 Bell-channel simulation, forensics, and API tests."""

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.auth import get_current_user
from api.auth_models import UserRole
from api.user_models import User
from quantum.channel import run_quantum_channel_experiment
from quantum.measurements import calculate_channel_metrics
from security.quantum_forensics import analyze_quantum_forensics


client = TestClient(app)
SCENARIOS = (
    "normal",
    "bit_flip",
    "phase_flip",
    "bit_phase_flip",
    "intercept_resend",
    "channel_noise",
)


@pytest.fixture(autouse=True)
def authorized_operator() -> None:
    operator = User(
        id=1,
        username="operator",
        email="operator@example.com",
        password_hash="not-used-by-dependency-override",
        role=UserRole.SECURITY_OPERATOR.value,
        is_active=True,
    )
    app.dependency_overrides[get_current_user] = lambda: operator
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def observed_scenarios() -> dict[str, dict]:
    """Run each seeded experiment once for stable, fast range assertions."""
    return {
        scenario: run_quantum_channel_experiment(scenario, shots=1024)
        for scenario in SCENARIOS
    }


def forensic_result(observed_scenarios: dict[str, dict], scenario: str) -> dict:
    return analyze_quantum_forensics(
        observed_scenarios[scenario]["measurements"]
    )


def test_clean_bell_circuit_has_strong_correlation(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["normal"]["measurements"]
    assert measurements["correlation_rate"] > 95.0
    assert set(measurements["z_basis_counts"]) == {"00", "01", "10", "11"}


def test_normal_channel_is_secure(observed_scenarios: dict[str, dict]) -> None:
    result = forensic_result(observed_scenarios, "normal")
    assert result["channel_status"] == "SECURE"
    assert result["attack_detected"] is False
    assert result["probable_attack"] is None


def test_bit_flip_changes_z_basis_statistics(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["bit_flip"]["measurements"]
    assert measurements["z_basis_error_rate"] > 90.0
    assert measurements["x_basis_error_rate"] < 10.0


def test_bit_flip_is_inferred_as_x_disturbance(
    observed_scenarios: dict[str, dict],
) -> None:
    result = forensic_result(observed_scenarios, "bit_flip")
    assert result["dominant_pauli_syndrome"] == "X"
    assert result["probable_attack"] == "BIT_FLIP"


def test_phase_flip_is_visible_in_x_basis(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["phase_flip"]["measurements"]
    assert measurements["z_basis_error_rate"] < 10.0
    assert measurements["x_basis_error_rate"] > 90.0


def test_phase_flip_is_inferred_as_z_disturbance(
    observed_scenarios: dict[str, dict],
) -> None:
    result = forensic_result(observed_scenarios, "phase_flip")
    assert result["dominant_pauli_syndrome"] == "Z"
    assert result["probable_attack"] == "PHASE_FLIP"


def test_bit_phase_flip_changes_both_bases(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["bit_phase_flip"]["measurements"]
    result = forensic_result(observed_scenarios, "bit_phase_flip")
    assert measurements["z_basis_error_rate"] > 90.0
    assert measurements["x_basis_error_rate"] > 90.0
    assert result["probable_attack"] == "BIT_PHASE_FLIP"
    assert result["dominant_pauli_syndrome"] == "Y"


def test_intercept_resend_reduces_complementary_basis_correlation(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["intercept_resend"]["measurements"]
    result = forensic_result(observed_scenarios, "intercept_resend")
    assert measurements["z_basis_error_rate"] < 10.0
    assert 35.0 < measurements["x_basis_error_rate"] < 65.0
    assert measurements["bell_correlation_score"] < 0.85
    assert result["probable_attack"] == "INTERCEPT_RESEND"


def test_channel_noise_creates_measurable_degradation(
    observed_scenarios: dict[str, dict],
) -> None:
    measurements = observed_scenarios["channel_noise"]["measurements"]
    result = forensic_result(observed_scenarios, "channel_noise")
    assert 5.0 < measurements["z_basis_error_rate"] < 30.0
    assert 5.0 < measurements["x_basis_error_rate"] < 30.0
    assert result["probable_attack"] == "CHANNEL_NOISE"
    assert result["channel_status"] == "DEGRADED"


def test_qber_calculation_is_combined_mismatch_percentage() -> None:
    metrics = calculate_channel_metrics(
        {"00": 40, "11": 40, "01": 10, "10": 10},
        {"00": 35, "11": 35, "01": 15, "10": 15},
    )
    assert metrics["qber"] == pytest.approx(25.0)


def test_correlation_calculation_is_correct() -> None:
    metrics = calculate_channel_metrics(
        {"00": 40, "11": 40, "01": 10, "10": 10},
        {"00": 35, "11": 35, "01": 15, "10": 15},
    )
    assert metrics["correlation_rate"] == pytest.approx(75.0)
    assert metrics["bell_correlation_score"] == pytest.approx(0.75)


def test_matching_and_mismatching_measurements_are_correct() -> None:
    metrics = calculate_channel_metrics(
        {"00": 40, "11": 40, "01": 10, "10": 10},
        {"00": 35, "11": 35, "01": 15, "10": 15},
    )
    assert metrics["matching_measurements"] == 150
    assert metrics["mismatching_measurements"] == 50
    assert metrics["total_measurements"] == 200


def test_quantum_status_endpoint() -> None:
    response = client.get("/api/quantum/status")
    assert response.status_code == 200
    result = response.json()
    assert result["module"] == "Quantum Threat Forensics"
    assert result["status"] == "ready"
    assert result["supported_scenarios"] == list(SCENARIOS)


def test_quantum_analyze_normal_endpoint() -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": "normal", "shots": 128},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["forensics"]["channel_status"] == "SECURE"
    assert result["detection_correct"] is True


def test_quantum_analyze_bit_flip_endpoint() -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": "bit_flip", "shots": 128},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["forensics"]["probable_attack"] == "BIT_FLIP"
    assert result["detection_correct"] is True


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_quantum_analyze_supports_every_scenario(scenario: str) -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": scenario, "shots": 128},
    )
    assert response.status_code == 200
    assert response.json()["detection_correct"] is True


def test_unknown_quantum_scenario_is_rejected() -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": "unknown", "shots": 1024},
    )
    assert response.status_code == 422


def test_quantum_shots_below_minimum_are_rejected() -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": "normal", "shots": 127},
    )
    assert response.status_code == 422


def test_quantum_shots_above_maximum_are_rejected() -> None:
    response = client.post(
        "/api/quantum/analyze",
        json={"scenario": "normal", "shots": 8193},
    )
    assert response.status_code == 422


def test_malformed_quantum_request_is_rejected() -> None:
    assert client.post("/api/quantum/analyze", json={}).status_code == 422
    assert client.post(
        "/api/quantum/analyze",
        json={"scenario": "normal", "shots": "1024"},
    ).status_code == 422
