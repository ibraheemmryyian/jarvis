from datetime import datetime, timedelta

def create_jwt(secret_key):
    def jwt_encode(payload):
        payload['exp'] = datetime.utcnow() + timedelta(minutes=30)
        return jwt.encode(payload, secret_key, algorithm='HS256')

    def jwt_decode(token):
        try:
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            return decoded
        except jwt.ExpiredSignatureError:
            return None

    return {
        'jwt_encode': jwt_encode,
        'jwt_decode': jwt_decode
    }