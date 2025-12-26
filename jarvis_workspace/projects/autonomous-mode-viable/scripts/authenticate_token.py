def authenticate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user = get_user(user_id)
        return user
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenException("Invalid token")

# Rest of the code...