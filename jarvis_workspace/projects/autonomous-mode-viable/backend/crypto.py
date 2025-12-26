import hashlib
from typing import Any

class Crypto:
    @staticmethod
    def sha256(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def md5(data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()

    @staticmethod
    def hash_string(string: str, algo: str = "sha256") -> str:
        if algo == "sha256":
            return hashlib.sha256(string.encode()).hexdigest()
        elif algo == "md5":
            return hashlib.md5(string.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algo}")

    @staticmethod
    def hash_file(file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @staticmethod
    def encrypt_data(data: Any) -> str:
        # Dummy implementation. In practice, use a secure encryption method.
        return Crypto.sha256(str(data))

    @staticmethod
    def decrypt_data(encrypted_data: str) -> Any:
        # Dummy implementation. In practice, use the same decryption method used for encryption.
        return int(encrypted_data, 16)