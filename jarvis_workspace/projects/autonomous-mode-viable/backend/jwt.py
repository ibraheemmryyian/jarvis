from datetime import datetime, timedelta

class JWT:
    @staticmethod
    def encode_token(payload: dict, secret_key: str) -> str:
        payload['exp'] = datetime.utcnow() + timedelta(minutes=30)
        return 'Bearer ' + jwt.encode(payload, secret_key, algorithm='HS256').decode('utf-8')

    @staticmethod
    def decode_token(token: str, secret_key: str) -> dict:
        try:
            token = token.replace("Bearer ", "")
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = RSA.import_key(open(secret_key).read())
            pem = rsa_key.export_key()
            payload = jwt.decode(token, pem, algorithms=['RS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return 'Token expired'
        except jwt.InvalidTokenError:
            return 'Invalid token'

    @staticmethod
    def decode_token_rsa(token: str, secret_key: str) -> dict:
        try:
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = RSA.import_key(open(secret_key).read())
            pem = rsa_key.export_key()
            payload = jwt.decode(token, pem, algorithms=['RS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return 'Token expired'
        except jwt.InvalidTokenError:
            return 'Invalid token'