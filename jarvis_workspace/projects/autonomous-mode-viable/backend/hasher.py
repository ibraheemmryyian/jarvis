from passlib.context import CryptContext

class Hasher(CryptContext):
    def hash_password(self, password: str) -> str:
        return self.hash(password + secrets.token_hex(16))