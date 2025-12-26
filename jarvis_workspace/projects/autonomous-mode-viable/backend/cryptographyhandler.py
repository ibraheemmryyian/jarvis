from cryptography.fernet import Fernet

class CryptographyHandler:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        return self.cipher_suite.decrypt(data.encode()).decode()