from passlib.hash import bcrypt

def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_text_password, hashed_password)