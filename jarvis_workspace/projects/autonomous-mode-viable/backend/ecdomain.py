import os
import hashlib
from typing import Tuple

class ECDomain:
    def __init__(self, curve: str = "secp256k1"):
        self.curve = curve
        self.domain = None
    
    def generate_private_key(self) -> bytes:
        # Generate a random private key for the specified elliptic curve
        return os.urandom(32)

    def get_public_key(self, private_key: bytes) -> Tuple[bytes, bytes]:
        # Convert the private key to a point on the curve
        private_key_int = int.from_bytes(private_key, byteorder="big")
        point = self.curve.generator * private_key_int
        
        # Serialize the public key as hex string
        x = point.x().hex()
        y = point.y().hex()
        return bytes.fromhex(x), bytes.fromhex(y)

    def sign(self, message: bytes, private_key: bytes) -> bytes:
        # Create a signature for the given message using the ECDSA algorithm
        digest = hashlib.sha256(message).digest()
        k = os.urandom(32)
        r, s = self.ecdsa_sign(digest, k)

        return r.pack() + s.pack()

    def ecdsa_sign(self, digest: bytes, k: bytes) -> Tuple[int, int]:
        # Perform the ECDSA signing operation
        k_int = int.from_bytes(k, byteorder="big")
        hash_int = int.from_bytes(digest, byteorder="big")

        G = self.curve.generator
        n = self.curve.order()

        r = 0
        while True:
            kG = G * k % n
            if not kG.is_infinite():
                r = kG.x().int()
                break

        s = (hash_int + r * self.domain) * k_inv % n
        return r, s

    def verify(self, message: bytes, signature: bytes, public_key: Tuple[bytes, bytes]) -> bool:
        # Verify the given signature for the message using the ECDSA algorithm
        digest = hashlib.sha256(message).digest()
        r, s = signature[:32], signature[32:]

        G = self.curve.generator
        n = self.curve.order()

        r_int = int.from_bytes(r, byteorder="big")
        s_int = int.from_bytes(s, byteorder="big")

        if not 1 < r_int < n or not 1 < s_int < n:
            return False

        hash_int = (s * self.domain - r * s) % n
        if hash_int != 0:
            hash_int_inv = pow(hash_int, n - 2, n)
        
        Gx, Gy = public_key
        x = int.from_bytes(Gx, byteorder="big")
        y = int.from_bytes(Gy, byteorder="big")

        if r != G * (hash_int * x + hash_int_inv * y) % n:
            return False

        return True

    def verify_signature(self, message: bytes, signature: bytes):
        # Verify the given signature for the message using the ECDSA algorithm
        public_key = self.get_public_key(signature[:32])
        return self.verify(message, signature, public_key)