import secrets

def generate_random_token(length=32):
    return secrets.token_hex(length)