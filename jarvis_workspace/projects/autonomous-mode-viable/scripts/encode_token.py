from base64 import encodebytes

def encode_token(token: str) -> str:
    encoded_bytes = encodebytes(token.encode()).decode()
    return f"Bearer {encoded_bytes}"