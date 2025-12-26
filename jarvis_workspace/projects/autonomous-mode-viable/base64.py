import io


def b64encode(data):
    """Base64 encode data."""
    with io.BytesIO(data) as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return encoded


def b64decode(encoded):
    """Base64 decode a string."""
    return base64.b64decode(encoded)


def b64urlsafe_encode(data):
    """URL-safe Base64 encode data."""
    with io.BytesIO(data) as f:
        encoded = base64.urlsafe_b64encode(f.read()).decode('utf-8')
    return encoded


def b64urlsafe_decode(encoded):
    """URL-safe Base64 decode a string."""
    return base64.urlsafe_b64decode(encoded)