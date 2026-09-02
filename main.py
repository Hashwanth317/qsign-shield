"""Q-Sign Shield V0.5 multi-attack security simulation."""

from attacks.forgery import simulate_forgery_attack
from attacks.impersonation import simulate_impersonation_attempt
from attacks.replay import simulate_replay_attack
from attacks.signature_tampering import simulate_signature_tampering
from quantum.qds import generate_quantum_signature
from security.detector import detect_security_event
from security.replay_guard import ReplayGuard


SIGNER = "Alice"
ATTACKER_IDENTITY = "Attacker"
ORIGINAL_MESSAGE = "TRANSFER 10000 TO BOB"
FORGED_MESSAGE = "TRANSFER 90000 TO BOB"


def short_hash(hash_value: str, length: int = 16) -> str:
    """Return a concise hash fingerprint for terminal output."""
    return f"{hash_value[:length]}..."


def print_detection(result: dict) -> None:
    """Print the common metrics returned by the V0.5 detector."""
    identity_status = "PASS" if result["identity_match"] else "FAIL"
    print(f"Attack Type: {result['attack_type']}")
    print(f"Cryptographic Signature: {result['cryptographic_signature']}")
    print(
        f"Matching Signature Bits: {result['matching_signature_bits']} / "
        f"{result['total_signature_bits']}"
    )
    print(f"Mismatching Signature Bits: {result['mismatching_signature_bits']}")
    print(f"Verification Percentage: {result['verification_percentage']:.2f}%")
    print(f"Claimed Sender: {result['sender_identity']}")
    print(f"Signature Owner: {result['signature_owner_identity']}")
    print(f"Identity Match: {identity_status}")
    print(f"Transaction ID: {result['transaction_id']}")
    print(f"Overall Verification: {result['overall_verification']}")
    print(f"Security Decision: {result['security_decision']}")


def main() -> None:
    """Generate one valid signature and demonstrate all five V0.5 scenarios."""
    print("=" * 52)
    print("                 Q-SIGN SHIELD V0.5")
    print("       Multi-Attack Quantum Security Simulation")
    print("=" * 52)

    print("\nGenerating the original QDS signature...")
    signature = generate_quantum_signature(
        signer=SIGNER,
        message=ORIGINAL_MESSAGE,
        sample_bits=16,
        shots=256,
    )
    print(f"Signature ready: {signature['signature_id']}")

    print("\n[1] LEGITIMATE TRANSACTION\n")
    print(f"Message:\n{ORIGINAL_MESSAGE}\n")
    legitimate = detect_security_event(SIGNER, ORIGINAL_MESSAGE, signature)
    print_detection(legitimate)

    print("\n" + "-" * 52)
    print("\n[2] MESSAGE FORGERY\n")
    forgery = simulate_forgery_attack(
        original_message=ORIGINAL_MESSAGE,
        forged_message=FORGED_MESSAGE,
        original_signature=signature,
    )
    forged_result = detect_security_event(
        SIGNER,
        forgery["forged_message"],
        forgery["reused_signature"],
    )
    print(f"Original:\n{forgery['original_message']}")
    print(f"\nForged:\n{forgery['forged_message']}")
    print(f"\nOriginal Hash: {short_hash(forgery['original_message_hash'])}")
    print(f"Forged Hash:   {short_hash(forgery['forged_message_hash'])}\n")
    print_detection(forged_result)

    print("\n" + "-" * 52)
    print("\n[3] SIGNATURE TAMPERING\n")
    tampering = simulate_signature_tampering(signature)
    tampered_result = detect_security_event(
        SIGNER,
        ORIGINAL_MESSAGE,
        tampering["tampered_signature"],
    )
    positions = ", ".join(str(position + 1) for position in tampering["tampered_positions"])
    print("Message unchanged")
    print(f"Signature bits modified at positions: {positions}\n")
    print_detection(tampered_result)

    print("\n" + "-" * 52)
    print("\n[4] REPLAY ATTACK\n")
    replay = simulate_replay_attack(ORIGINAL_MESSAGE, signature)
    replay_guard = ReplayGuard()
    first = detect_security_event(
        SIGNER,
        replay["first_submission"]["message"],
        replay["first_submission"]["signature"],
        replay_guard=replay_guard,
    )
    second = detect_security_event(
        SIGNER,
        replay["replayed_submission"]["message"],
        replay["replayed_submission"]["signature"],
        replay_guard=replay_guard,
    )
    print(f"Transaction submitted once: {first['submission_status']}")
    print(f"Same transaction submitted again: {second['submission_status']}\n")
    print_detection(second)

    print("\n" + "-" * 52)
    print("\n[5] IMPERSONATION ATTEMPT\n")
    impersonation = simulate_impersonation_attempt(ATTACKER_IDENTITY, signature)
    impersonation_result = detect_security_event(
        impersonation["claimed_sender"],
        ORIGINAL_MESSAGE,
        impersonation["reused_signature"],
    )
    print_detection(impersonation_result)
    print("\n" + "=" * 52)


if __name__ == "__main__":
    main()
