from passlib.context import CryptContext

class PasswordHasher:
    def __init__(self):
        self.password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.password_context.hash(password)

    def verify(self, hashed_password: str, plain_text_password: str) -> bool:
        try:
            return self.password_context.verify(hashed_password, plain_text_password)
        except Exception as e:
            return False