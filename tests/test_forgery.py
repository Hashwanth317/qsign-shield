"""V0.4 forgery-detection behavior tests."""

import unittest

from attacks.forgery import simulate_forgery_attack
from quantum.qds import generate_quantum_signature
from security.detector import detect_forgery


class ForgeryDetectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.signer = "Alice"
        cls.original_message = "TRANSFER 10000 TO BOB"
        cls.forged_message = "TRANSFER 90000 TO BOB"
        cls.signature = generate_quantum_signature(
            cls.signer,
            cls.original_message,
            sample_bits=16,
            shots=256,
        )

    def test_legitimate_message_passes(self) -> None:
        result = detect_forgery(
            self.signer, self.original_message, self.signature
        )
        self.assertEqual(result["signature_verification"], "PASS")
        self.assertEqual(result["security_decision"], "LEGITIMATE")

    def test_modified_message_with_original_signature_fails(self) -> None:
        attack = simulate_forgery_attack(
            self.original_message, self.forged_message, self.signature
        )
        self.assertIs(attack["reused_signature"], self.signature)

        result = detect_forgery(
            self.signer, attack["forged_message"], attack["reused_signature"]
        )
        self.assertEqual(result["signature_verification"], "FAIL")
        self.assertEqual(result["security_decision"], "FORGERY DETECTED")

    def test_unchanged_message_is_not_forgery(self) -> None:
        result = detect_forgery(
            self.signer, self.original_message, self.signature
        )
        self.assertNotEqual(result["security_decision"], "FORGERY DETECTED")


if __name__ == "__main__":
    unittest.main()
