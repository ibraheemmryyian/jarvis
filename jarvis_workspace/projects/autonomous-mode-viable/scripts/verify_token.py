from jose import JWTError, jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        username: str = payload.get("sub")
        
        if not username or username != token_data.username:
            raise JWSError
            
        return True
    except JWTError as e:
        raise JWSError from e