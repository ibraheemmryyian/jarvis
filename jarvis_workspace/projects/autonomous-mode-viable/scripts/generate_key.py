import os
from typing import List, Tuple

def generate_key():
    return os.urandom(32)

def sign(message: bytes, private_key: bytes) -> bytes:
    key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    signer = key.get_verifying_key()
    signature = key.sign(message)
    return signature

def verify(message: bytes, public_key: bytes, signature: bytes) -> bool:
    verifier = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)
    try:
        verifier.verify(signature, message)
        return True
    except ecdsa.BadSignatureError:
        return False

def generate_address(private_key: bytes) -> str:
    hash160 = ripemd160(sha256(private_key))
    network_byte = 0x00 if is_compressed else 0x01
    return "1" + hex_string(network_byte + hash160)

def derive_public_keys(private_key: bytes, compressed: bool = False) -> Tuple[bytes, bytes]:
    raw_pubkey = SigningKey.from_string(
        private_key, curve=ecdsa.SECP256k1).get_verifying_key().to_string()
    if compressed:
        pub_key_compressed = raw_pubkey[1:] + b'\x01' if raw_pubkey[0] else b'\x02'
    else:
        pub_key_uncompressed = b"\04" + raw_pubkey
    return (pub_key_compressed, pub_key_uncompressed)

def sha256(data: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(data)
    return h.digest()

def ripemd160(data: bytes) -> bytes:
    h = hashlib.new("ripemd160")
    h.update(data)
    return h.digest()

def hex_string(data: bytes) -> str:
    return data.hex()