from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister,
    transpile
)
from qiskit_aer import AerSimulator


def build_teleportation_circuit(secret_bit=1):
    """
    Build a 3-qubit quantum teleportation circuit.

    q0 -> Alice's secret qubit
    q1 -> Alice's Bell-pair qubit
    q2 -> Bob's Bell-pair qubit

    Classical bits:
    c0 -> Alice measurement from q0
    c1 -> Alice measurement from q1
    c2 -> Bob's final measurement
    """

    q = QuantumRegister(3, "q")
    c = ClassicalRegister(3, "c")

    circuit = QuantumCircuit(q, c)

    # ----------------------------------------
    # STEP 1: Prepare Alice's secret bit
    # ----------------------------------------

    if secret_bit == 1:
        circuit.x(q[0])

    circuit.barrier()

    # ----------------------------------------
    # STEP 2: Create Bell Pair
    # ----------------------------------------

    circuit.h(q[1])
    circuit.cx(q[1], q[2])

    circuit.barrier()

    # ----------------------------------------
    # STEP 3: Alice performs teleportation
    # ----------------------------------------

    circuit.cx(q[0], q[1])
    circuit.h(q[0])

    circuit.barrier()

    # ----------------------------------------
    # STEP 4: Alice measures q0 and q1
    # ----------------------------------------

    circuit.measure(q[0], c[0])
    circuit.measure(q[1], c[1])

    # ----------------------------------------
    # STEP 5: Bob applies Pauli corrections
    # ----------------------------------------

    # If Alice's q1 measurement is 1,
    # Bob applies X correction.
    with circuit.if_test((c[1], True)):
        circuit.x(q[2])

    # If Alice's q0 measurement is 1,
    # Bob applies Z correction.
    with circuit.if_test((c[0], True)):
        circuit.z(q[2])

    circuit.barrier()

    # ----------------------------------------
    # STEP 6: Bob measures final qubit
    # ----------------------------------------

    circuit.measure(q[2], c[2])

    return circuit


def run_teleportation(secret_bit=1, shots=256):
    """
    Run the teleportation circuit and return
    Bob's received bit and success rate.
    """

    circuit = build_teleportation_circuit(secret_bit)

    simulator = AerSimulator()

    compiled_circuit = transpile(
        circuit,
        simulator
    )

    job = simulator.run(
        compiled_circuit,
        shots=shots
    )

    result = job.result()

    counts = result.get_counts(compiled_circuit)

    correct_results = 0

    bob_0 = 0
    bob_1 = 0

    # Qiskit displays the classical bits as c2 c1 c0.
    # Therefore, the first bit belongs to Bob.
    for bit_string, count in counts.items():

        clean_bits = bit_string.replace(" ", "")

        bob_result = int(clean_bits[0])

        if bob_result == 0:
            bob_0 += count
        else:
            bob_1 += count

        if bob_result == secret_bit:
            correct_results += count

    success_rate = correct_results / shots

    # Choose whichever result Bob measured more often.
    received_bit = 0 if bob_0 > bob_1 else 1

    return {
        "secret_bit": secret_bit,
        "received_bit": received_bit,
        "shots": shots,
        "counts": counts,
        "success_rate": success_rate,
        "circuit": circuit
    }