from jose import jwt
from datetime import datetime, timedelta

def generate_jwt_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=15)})
    return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")