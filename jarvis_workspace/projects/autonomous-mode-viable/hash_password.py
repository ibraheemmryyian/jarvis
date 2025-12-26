from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hash(password)