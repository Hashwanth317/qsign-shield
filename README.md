# Q-Sign Shield

Q-Sign Shield is an educational SIH26141 prototype that combines a Qiskit Aer
quantum-teleportation simulation, simulated quantum digital signatures,
multi-attack transaction checks, a FastAPI backend, and a React dashboard.

## Current modules

- V0.1: quantum teleportation
- V0.2: SHA-256 encoding and multi-bit teleportation
- V0.3: educational QDS generation and verification
- V0.4: message-forgery detection
- V0.5: forgery, signature tampering, replay, and impersonation simulation
- V0.6: FastAPI interface
- V0.7: React dashboard
- V0.8: quantum-channel threat forensics
- V0.9: React quantum-forensics dashboard integration

## V0.8 Quantum Channel Threat Forensics

V0.8 prepares the Bell reference state
`|Phi+> = (|00> + |11>) / sqrt(2)` and measures independent experiments in
both the Z and X bases. An ideal pair produces correlated `00` and `11`
outcomes in either basis. The X-basis check applies a Hadamard rotation to
both qubits immediately before computational-basis measurement.

The simulator includes these controlled scenarios:

- **Normal:** no intentional disturbance.
- **Bit flip:** Pauli X on the transmitted qubit, disrupting Z correlation.
- **Phase flip:** Pauli Z; invisible to the Z check but exposed by X analysis.
- **Bit + phase flip:** Pauli Y, disrupting both complementary-basis checks.
- **Intercept-resend:** Eve measures in Z, resets the intercepted qubit, and
  prepares the measured value. Z statistics remain classically correlated,
  while the X check reveals the lost coherence.
- **Channel noise:** an Aer Pauli noise model applies controlled random I/X/Y/Z
  errors to model accidental degradation.

### Metrics

- **Z/X basis error rates:** mismatched `01` and `10` outcomes divided by the
  shots in that basis.
- **QBER:** all Z- and X-basis mismatches divided by all measurements across
  both independent experiments.
- **Correlation rate:** all correlated `00` and `11` observations divided by
  all measurements across both bases.
- **Bell correlation score:** correlation rate divided by 100, giving a direct
  normalized observed-correlation score from 0 to 1.
- **Measurement fidelity:** the observed two-basis agreement percentage. It is
  a shot-based reference metric and is **not** quantum-state fidelity.
- **Pauli syndrome evidence:** X evidence comes from excess Z-basis error, Z
  evidence from excess X-basis error, and Y evidence from errors shared across
  both bases.

The explainable classifier only receives these observed statistics. The
simulated scenario remains separate and is compared with the prediction only
after classification. Central thresholds live in `security/config.py` and are
educational prototype settings, not production quantum-network standards.

Some physical processes can produce similar statistics. In particular,
limited Z/X correlation data cannot uniquely identify every possible quantum
channel or adversary. Full process tomography, authenticated protocols, and
hardware calibration are outside this prototype.

## Run locally

```bash
source .venv/bin/activate
python -m pytest
python demo_quantum_forensics.py
python -m uvicorn api.app:app --reload
```

The V0.8 API endpoints are:

- `GET /api/quantum/status`
- `POST /api/quantum/analyze`

Example request:

```json
{
  "scenario": "phase_flip",
  "shots": 1024
}
```

Allowed shot counts are 128 through 8192.

## V0.9 Quantum Forensics Dashboard

The React dashboard consumes the V0.8 endpoints directly and does not duplicate
the classifier in JavaScript. Its Quantum Channel Security layer provides:

- six selectable simulator scenarios and validated shot controls;
- secure, degraded, and compromised channel status cards;
- QBER, Z/X error, correlation, and measurement-fidelity visuals;
- backend-derived Pauli syndrome evidence and detection explanations;
- collapsible measurement counts;
- an on-demand clean-channel comparison; and
- session-only quantum events and alert counters alongside transaction events.

The comparison uses CSS bars rather than an additional chart dependency. If the
backend becomes unavailable, the quantum panel removes prior results and shows
an explicit offline state instead of presenting cached metrics as current.

> This project is a Qiskit Aer-based educational simulation. It does not send
> physical qubits, implement production QKD, or represent a deployed quantum
> network.
