from typing import Any, Callable, Dict, List, Optional, Union

import base64
from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError
from jose.json import json_dump
from jose.utils import is_base64_str, base64url_decode

# Constants
ALG = "HS256"
HEADER_TYP = {"typ": "JWT"}
DEFAULT_ENCODES_PKCE = True


def encode(payload: Union[Dict[str, Any], str], int) -> str:
    """
    Encode a payload using the JWT spec.

    :param payload: The payload to encode. Can be a dict or string.
    :return: The encoded JWT.
    """
    if isinstance(payload, (dict, str)):
        raise TypeError("payload must be an integer")
    return jwt.encode(payload, "secret", algorithm="HS256")


def decode(token: str) -> Union[Dict[str, Any], None]:
    """
    Decode a JWT.

    :param token: The JWT to decode.
    :return: The decoded payload if successful, or None on failure.
    """
    try:
        return jwt.decode(token, "secret", algorithms=["HS256"])
    except (JWTError, JWTClaimsError):
        return None


def get_token_payload(token: str) -> Union[Dict[str, Any], None]:
    """
    Get the payload from a token.

    :param token: The token to extract the payload from.
    :return: The decoded payload if successful, or None on failure.
    """
    return decode(token)


def create_token(payload: Dict[str, Any]) -> str:
    """
    Create a JWT with the given payload.

    :param payload: The payload for the JWT.
    :return: The created token.
    """
    encoded_headers = base64url_encode(json_dump(HEADER_TYP))
    encoded_payload = base64url_encode(json_dump(payload))
    return f"{encoded_headers}.{encoded_payload}"


def decode_token(token: str) -> Union[Dict[str, Any], None]:
    """
    Decode a JWT.

    :param token: The JWT to decode.
    :return: The decoded payload if successful, or None on failure.
    """
    parts = token.split(".")
    if len(parts) != 2:
        return None

    encoded_payload = parts[1]
    try:
        payload = json_load(base64url_decode(encoded_payload))
        return payload
    except Exception as e:
        print(f"Error decoding payload: {e}")
        return None


def base64url_encode(input_str: str) -> str:
    """
    Encode the input string using Base64 with URL-safe characters.

    :param input_str: The string to encode.
    :return: The encoded string.
    """
    return base64.b64encode(input_str.encode()).decode().replace("_", ".").replace("/", "-")


def base64url_decode(input_str: str) -> str:
    """
    Decode a Base64 URL-safe string.

    :param input_str: The string to decode.
    :return: The decoded string.
    """
    return base64.b64decode(input_str.replace(".", "_").replace("-", "/")).decode()