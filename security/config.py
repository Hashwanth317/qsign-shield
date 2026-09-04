"""Central configuration for the V0.8 quantum forensics prototype.

These thresholds are educational prototype settings chosen for the controlled
Aer scenarios in this repository. They are not production quantum-network,
QKD, or hardware-calibration standards.
"""

DEFAULT_CHANNEL_SHOTS = 1024
MIN_CHANNEL_SHOTS = 128
MAX_CHANNEL_SHOTS = 8192
DEFAULT_SIMULATOR_SEED = 26141

# A clean simulator should be close to zero error in both measured bases.
QBER_WARNING_THRESHOLD = 5.0
QBER_ATTACK_THRESHOLD = 35.0
CORRELATION_MINIMUM = 95.0
FIDELITY_MINIMUM = 95.0

# Explainable pattern boundaries for the controlled Pauli scenarios.
PAULI_STRONG_ERROR_MINIMUM = 75.0
PAULI_CLEAN_BASIS_MAXIMUM = 20.0

# A Z-basis intercept/resend operation preserves Z correlations but produces
# approximately 50% error when the pair is checked in the X basis.
INTERCEPT_RESEND_ERROR_MINIMUM = 35.0
INTERCEPT_RESEND_ERROR_MAXIMUM = 65.0
INTERCEPT_RESEND_PRESERVED_BASIS_MAXIMUM = 15.0

