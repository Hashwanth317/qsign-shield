# Q-Sign Shield

Q-Sign Shield is an educational SIH26141 prototype that combines a Qiskit Aer
quantum-teleportation simulation, simulated quantum digital signatures,
multi-attack transaction checks, a FastAPI backend, and a React dashboard.

The application also includes PostgreSQL-backed user accounts, Argon2id
password hashing, JWT access tokens, protected dashboard routes, and backend
role enforcement for transaction users and security operators.

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

## Authentication and roles

- **Transaction users** can sign and verify transactions and view their result.
- **Security operators** can also run attack simulations, inspect security
  events, and access quantum-channel forensics.
- Public registration creates transaction users. Security-operator registration
  is disabled unless `ALLOW_OPERATOR_REGISTRATION=true`; the demo seed script is
  the preferred prototype setup path.
- Passwords are stored only as Argon2id hashes. JWTs contain the user subject and
  role and expire after the configured access-token lifetime.

The authentication API is:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

`/health`, registration, and login are public. Transaction signing and
verification require an active authenticated user. Security checks and quantum
forensics require the `security_operator` role.

## PostgreSQL and environment setup

Create a PostgreSQL database locally, on Render, or on Neon. Copy the example
configuration without committing the resulting `.env` file:

```bash
cp .env.example .env
```

Set these backend values:

- `DATABASE_URL`: PostgreSQL URL; `postgres://` and `postgresql://` Render/Neon
  forms are normalized to the psycopg 3 driver.
- `JWT_SECRET_KEY`: a long random deployment secret.
- `JWT_ALGORITHM`: `HS256` by default.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `60` by default.
- `DEMO_USER_PASSWORD` and `DEMO_OPERATOR_PASSWORD`: required only while
  running the demo seed command.

The frontend uses `frontend/.env` with:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Production must set `VITE_API_BASE_URL` to the deployed Render API URL.

## Seed demo users

After setting both demo password variables, run the idempotent seed command:

```bash
python -m scripts.seed_users
```

It creates `user` with role `transaction_user` and `operator` with role
`security_operator` only when they do not already exist. It never prints
passwords, hashes, or secrets.

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
pip install -r requirements.txt
python -m scripts.seed_users
python -m pytest
python demo_quantum_forensics.py
python -m uvicorn api.app:app --reload --env-file .env
```

Run the frontend separately:

```bash
cd frontend
npm install
npm run dev
```

## Render and Vercel deployment

For Render, attach a PostgreSQL database and configure `DATABASE_URL`,
`JWT_SECRET_KEY`, `JWT_ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`. Use
`pip install -r requirements.txt` as the build command and
`uvicorn api.app:app --host 0.0.0.0 --port $PORT` as the start command. Run
`python -m scripts.seed_users` once from a secure Render shell if demo accounts
are required.

For Vercel, keep the project root set to `frontend`, build with `npm run build`,
publish `dist`, and set `VITE_API_BASE_URL` to the Render service URL. The
included `frontend/vercel.json` preserves `/login` and `/dashboard` on direct
loads and refreshes. The FastAPI CORS configuration already allows
`https://qsign-shield.vercel.app` and Vercel preview domains.

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
