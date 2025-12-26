from cryptography.hazmat.primitives.asymmetric import ec

class Task:
    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def generate_private_key() -> ec.EllipticCurvePrivateKey:
        return ec.generate_private_key(ec.SECP256R1())

    @staticmethod
        def generate_public_key(private_key: ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
            return private_key.public_key()