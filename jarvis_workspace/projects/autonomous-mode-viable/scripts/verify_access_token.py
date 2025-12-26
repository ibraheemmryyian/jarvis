from jose import jwt

def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['RS256'])
    except exceptions.JWSError as e:
        raise InvalidSignatureError from e