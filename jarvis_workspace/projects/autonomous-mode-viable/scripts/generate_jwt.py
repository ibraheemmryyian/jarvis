from jose import jwt

def generate_jwt(claims, key):
    try:
        return jwt.encode(claims, key, algorithm='RS256')
    except exceptions.JWSError as e:
        raise InvalidSignatureError from e