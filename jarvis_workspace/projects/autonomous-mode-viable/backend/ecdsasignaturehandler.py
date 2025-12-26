from cryptography.hazmat.primitives.asymmetric import ec

class ECDSASignatureHandler:
    def __init__(self):
        self.curve = ec.SECP256K1()
        self.hash = SHA256()

    def generate_keys(self) -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        private_key = ec.generate_private_key(self.curve)
        public_key = private_key.public_key()
        return (private_key, public_key)

    def sign(private_key: ec.EllipticCurvePrivateKey, data: bytes) -> bytes:
        return private_key.sign(data, self.hash)

    def verify(public_key: ec.EllipticCurvePublicKey, signature: bytes, data: bytes) -> bool:
        try:
            public_key.verify(signature, data, self.hash)
            return True
        except InvalidSignature:
            return False