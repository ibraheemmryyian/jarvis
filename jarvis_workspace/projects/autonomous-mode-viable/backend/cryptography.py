import hashlib
from typing import Any, Union

def hash_string(string: str) -> str:
    return hashlib.sha256(string.encode()).hexdigest()

class Cryptography:
    @staticmethod
    def encrypt_data(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return hash_string(data)

    @staticmethod
    def decrypt_data(encrypted_data: str) -> Any:
        hashed_bytes = bytearray.fromhex(encrypted_data)
        decrypted_str = bytes(hashed_bytes).decode()
        return decrypted_str

    @staticmethod
    def generate_hash(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = hash_string(data)
        return data