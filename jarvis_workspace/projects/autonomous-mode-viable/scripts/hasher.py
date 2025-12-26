import secrets

def hasher(password):
    return pbkdf2_sha256.hash(password)

def verify_password(hashed_password, plain_text_password):
    return pbkdf2_sha256.verify(plain_text_password, hashed_password)

# Your code here...