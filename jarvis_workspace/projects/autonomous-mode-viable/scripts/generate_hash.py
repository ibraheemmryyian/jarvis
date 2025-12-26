# Assuming you're using passlib for hashing. You might need to install it.
from passlib.hash import bcrypt

def generate_hash(password: str):
    return bcrypt.hash(password)