from datetime import datetime, timedelta

def generate_access_token(data):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, "secret", algorithm="HS256")
    return encoded_jwt

def verify_access_token(token):
    try:
        decoded_jwt = jwt.decode(token, "secret", algorithms=["HS256"])
        return decoded_jwt
    except:
        return None

def generate_refresh_token(data):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, "secret", algorithm="HS256")
    return encoded_jwt

def verify_refresh_token(token):
    try:
        decoded_jwt = jwt.decode(token, "secret", algorithms=["HS256"])
        return decoded_jwt
    except:
        return None