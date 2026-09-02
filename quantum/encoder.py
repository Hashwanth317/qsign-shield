import hashlib


def hash_message(message):
    """
    Generate SHA-256 hash.
    """

    return hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()


def hash_to_binary(hash_value):
    """
    Convert hexadecimal hash into 256-bit binary.
    """

    return bin(
        int(hash_value, 16)
    )[2:].zfill(256)


def encode_message(message, sample_bits=8):
    """
    Convert a message into a SHA-256 fingerprint
    and select a small number of bits for simulation.
    """

    hash_value = hash_message(message)

    binary_hash = hash_to_binary(hash_value)

    selected_bits = binary_hash[:sample_bits]

    return {
        "message": message,
        "hash": hash_value,
        "binary": binary_hash,
        "selected_bits": selected_bits
    }