import os
import sys
from typing import Any, List, Optional, Tuple

# Constants
_CURVE_SECP256K1 = 24
_CURVE_P256 = 28

# ECDSA functions
def sign(data: bytes, private_key: int) -> bytes:
    """
    Sign the given data using the provided private key.
    
    :param data: The data to be signed.
    :param private_key: The private key for signing.
    :return: The signature of the data.
    """
    # Import necessary functions from ecdsa library
    from ecdsa import SigningKey, SECP256k1, NIST384p
    
    # Convert private key to SigningKey object
    sk = SigningKey.from_string(os.urandom(32), curve=SECP256k1)
    
    # Set the private key and sign data
    signature = sk.sign(data)
    
    return signature

def verify(signature: bytes, data: bytes, public_key: int) -> bool:
    """
    Verify the given signature for the provided data using the public key.
    
    :param signature: The signature to be verified.
    :param data: The data that was signed.
    :param public_key: The public key for verification.
    :return: True if the signature is valid, False otherwise.
    """
    # Import necessary functions from ecdsa library
    from ecdsa import SECP256k1
    
    # Convert public key to VerifyingKey object and sign data
    vk = SigningKey.from_string(os.urandom(32), curve=SECP256k1).verifying_key()
    
    # Verify the signature
    return vk.verify(signature, data)

def generate_keys() -> Tuple[bytes, int]:
    """
    Generate a new ECDSA key pair.
    
    :return: A tuple containing the private and public keys.
    """
    from ecdsa import SigningKey, SECP256k1
    
    # Generate a new signing key
    sk = SigningKey.generate(curve=SECP256k1)
    
    # Get the private key
    private_key = int(sk.to_string(), 2)
    
    # Get the public key
    public_key = bytes(sk.verifying_key.to_string())
    
    return private_key, public_key

def get_curve_name(curve: int) -> str:
    """
    Return the name of the elliptic curve based on the provided constant.
    
    :param curve: The curve constant.
    :return: The name of the elliptic curve.
    """
    if curve == _CURVE_SECP256K1:
        return "SECP256k1"
    elif curve == _CURVE_P256:
        return "P-256"
    else:
        raise ValueError(f"Unknown curve constant: {curve}")

def get_curve(curve_name: str) -> int:
    """
    Return the corresponding constant for the provided elliptic curve name.
    
    :param curve_name: The name of the elliptic curve.
    :return: The constant representing the elliptic curve.
    """
    if curve_name == "SECP256k1":
        return _CURVE_SECP256K1
    elif curve_name == "P-256":
        return _CURVE_P256
    else:
        raise ValueError(f"Unknown curve name: {curve_name}")