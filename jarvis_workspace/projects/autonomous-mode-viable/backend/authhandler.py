from passlib.context import CryptContext

class AuthHandler(CryptContext):
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.verify(plain_password + secrets.token_hex(16), hashed_password)