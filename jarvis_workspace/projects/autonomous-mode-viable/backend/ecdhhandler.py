from cryptography.hazmat.primitives.asymmetric import ec

class ECDHHandler:
    def __init__(self):
        self.curve = ec.SECP256K1()

    def generate_keys(self) -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
        private_key = ec.generate_private_key(self.curve)
        public_key = private_key.public_key()
        return (private_key, public_key)

    def derive_shared_secret(private_key: ec.EllipticCurvePrivateKey, peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
        return private_key.exchange(ec.ECDH, peer_public_key)