import os
from typing import Any, Union
from ecdsa import SigningKey, VerifyingKey, BadSignatureError

class ECDSASignature:
    def __init__(self, r: int, s: int, recovery_param: int = None) -> None:
        self.r = r
        self.s = s
        self.recovery_param = recovery_param

    @classmethod
    def from_bytes(cls, signature: bytes) -> 'ECDSASignature':
        r, s = signature[1:-1].split(b',')
        return cls(int.from_bytes(r, byteorder='big'), int.from_bytes(s, byteorder='big'))

    def to_bytes(self) -> bytes:
        return b','.join([self.r.to_bytes(32, byteorder='big'),
                          self.s.to_bytes(32, byteorder='big')])

class ECDSASigner:
    def __init__(self, private_key: SigningKey):
        self.private_key = private_key

    def sign(self, data: Union[bytes, str]) -> ECDSASignature:
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        return ECDSASignature(*self.private_key.sign(data))

    def sign_recoverable(self, data: Union[bytes, str], recovery_param: int) -> tuple[Any, Any]:
        if isinstance(data, str):
            data = bytes(data, 'utf-8')
        return self.private_key.sign_recoverable(data, recovery_param=recovery_param)

class ECDSAVerifier:
    def __init__(self, public_key: VerifyingKey):
        self.public_key = public_key

    def verify(self, signature: ECDSASignature, data: bytes) -> bool:
        return self.public_key.verify(signature.r, signature.s, data)

    def verify_recoverable(self, signature: tuple[Any, Any], recovery_param: int, data: bytes) -> bool:
        try:
            vk = self.public_key.from_der()
            vk.set_recovering_flag(True)
            return vk.verify_recovery(*signature, recovery_param=recovery_param, data=data)
        except BadSignatureError:
            return False