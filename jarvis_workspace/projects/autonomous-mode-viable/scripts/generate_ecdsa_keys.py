from cryptography.hazmat.primitives.asymmetric import ec

def generate_ecdsa_keys() -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    private_key = ec.generate_private_key(ec.SECP256K1())
    public_key = private_key.public_key()
    return (private_key, public_key)