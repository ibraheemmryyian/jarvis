def hash_password(password: str):
    hashed_password = password_hasher.hash(password)
    return hashed_password

# Rest of the code...