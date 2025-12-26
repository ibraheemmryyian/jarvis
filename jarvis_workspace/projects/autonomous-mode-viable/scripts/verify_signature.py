from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

def verify_signature(data: bytes, signature: bytes, public_key):
    try:
        public_key.verify(
            serialization.load_pem_private_key(signature, default_backend()),
            data,
            ec.ECDSA(ec.SECP256R1())
        )
    except InvalidSignature:
        return False
    else:
        return True