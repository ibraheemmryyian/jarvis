from typing import Any, Dict, List, Optional, Union
import base64
import json
import jwt
import time

def generate_token(payload: Dict[str, Any], secret_key: str) -> str:
    """
    Generate a JWT token.

    Args:
        payload (Dict[str, Any]): The payload of the token.
        secret_key (str): The secret key to sign the token.

    Returns:
        str: The generated JWT token.
    """
    try:
        encoded_payload = json.dumps(payload).encode("utf-8")
        header = {"alg": "HS256"}
        encoded_header = base64.b64urlencode(json.dumps(header))
        timestamp = int(time.time())
        claims = {
            "exp": timestamp + 3600,
            "iat": timestamp,
            "iss": "jarvis",
            "https://hasura.io/jwt/claims": {
                "sub": payload["user_id"],
            },
        }
        encoded_claims = base64.b64urlencode(json.dumps(claims))
        to_encode = f"{encoded_header}.{encoded_claims}"
        secret_key_bytes = secret_key.encode("utf-8")
        token = jwt.encode(to_encode, secret_key_bytes, "PS256")
        return token.decode("utf-8")
    except Exception as e:
        print(f"Error generating token: {str(e)}")
        return None

def decode_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token.

    Args:
        token (str): The JWT token to decode.
        secret_key (str): The secret key used for signing the token.

    Returns:
        Dict[str, Any] or None: The decoded payload of the token if successful,
            otherwise None.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        method = "PS256"
        header = {
            "alg": "HS256",
            "typ": "JWT",
        }
        encoded_header = base64.b64decode(header)
        claims = None
        payload = None

        start_time = time.time()
        msg = base64.urlsafe_b64decode(unverified_header["kid"])
        public_key = rsa.import_pkcs1(msg, "PEM")
        result = jwt.decode(token.encode(), public_key, algorithms=[method])
        return result
    except jwt.ExpiredSignatureError:
        print("Token expired. Please log in again.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token. Please check your credentials.")
        return None
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return None

def generate_refresh_token(payload: Dict[str, Any], secret_key: str) -> str:
    """
    Generate a refresh JWT token.

    Args:
        payload (Dict[str, Any]): The payload of the token.
        secret_key (str): The secret key to sign the token.

    Returns:
        str: The generated JWT token.
    """
    try:
        encoded_payload = json.dumps(payload).encode("utf-8")
        header = {"alg": "HS256"}
        encoded_header = base64.b64urlencode(json.dumps(header))
        timestamp = int(time.time())
        claims = {
            "exp": timestamp + 86400,
            "iat": timestamp,
            "iss": "jarvis",
            "https://hasura.io/jwt/claims": {
                "sub": payload["user_id"],
            },
        }
        encoded_claims = base64.b64urlencode(json.dumps(claims))
        to_encode = f"{encoded_header}.{encoded_claims}"
        secret_key_bytes = secret_key.encode("utf-8")
        token = jwt.encode(to_encode, secret_key_bytes, "PS256")
        return token.decode("utf-8")
    except Exception as e:
        print(f"Error generating refresh token: {str(e)}")
        return None

def decode_refresh_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT refresh token.

    Args:
        token (str): The JWT refresh token to decode.
        secret_key (str): The secret key used for signing the token.

    Returns:
        Dict[str, Any] or None: The decoded payload of the token if successful,
            otherwise None.
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        method = "HS256"
        header = {
            "alg": "HS256",
            "typ": "JWT",
        }
        encoded_header = base64.b64decode(header)
        claims = None
        payload = None

        start_time = time.time()
        msg = base64.urlsafe_b64decode(unverified_header["kid"])
        public_key = rsa.import_pkcs1(msg, "PEM")
        result = jwt.decode(token.encode(), public_key, algorithms=[method])
        return result
    except jwt.ExpiredSignatureError:
        print("Refresh token expired. Please log in again.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid refresh token. Please check your credentials.")
        return None
    except Exception as e:
        print(f"Error decoding refresh token: {str(e)}")
        return None