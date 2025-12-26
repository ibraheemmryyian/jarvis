import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

class ECDH:
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_private_key(self, curve=ec.SECP256R1()):
        self.private_key = ec.generate_private_key(curve)
        return self.private_key
    
    def generate_public_key(self):
        if not self.private_key:
            raise ValueError("Private key must be set first")
        self.public_key = self.private_key.public_key()
        return self.public_key

    def derive_shared_secret(self, peer_public_key):
        if not isinstance(peer_public_key, ec.EllipticCurvePublicKey):
            raise TypeError("Peer public key must be an EllipticCurvePublicKey")
        
        shared_secret = self.private_key.exchange(ec.ECDH, peer_public_key)
        return shared_secret

class ECDSA:
    def __init__(self, private_key: ec.EllipticCurvePrivateKey):
        self.private_key = private_key
        self.public_key = private_key.public_key()
    
    def sign(self, data_to_sign: bytes) -> bytes:
        signature = self.private_key.sign(
            data_to_sign,
            ec.ECDSA(ec.SECP256R1())
        )
        return signature
    
    def verify(self, data: bytes, signature: bytes):
        try:
            self.public_key.verify(signature, data, ec.ECDSA(ec.SECP256R1()))
            return True
        except InvalidSignature:
            return False

def generate_ecdsa_keys():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

def sign_data(private_key: ec.EllipticCurvePrivateKey, data: bytes) -> bytes:
    signature = private_key.sign(data, ec.ECDSA(ec.SECP256R1()))
    return signature

def verify_signature(public_key: ec.EllipticCurvePublicKey, data: bytes, signature: bytes):
    try:
        public_key.verify(signature, data, ec.ECDSA(ec.SECP256R1()))
        return True
    except InvalidSignature:
        return False