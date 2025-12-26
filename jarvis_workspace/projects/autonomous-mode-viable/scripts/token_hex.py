import secrets

def token_hex(length: int) -> str:
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(length))