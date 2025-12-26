from passlib.hash import pbkdf2_sha256

def get_hashed_password(password: str):
    return pbkdf2_sha256.hash(password)