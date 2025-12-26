from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import base64
import json
import jwt
from jose import JWTError, algorithms
from jose.utils import slip

# Define the token payload types
TokenPayload = Dict[str, Any]

class Jose:
    def __init__(self):
        pass

    # Encode a payload into a JWT
    def encode_jwt(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
        expires_delta: Optional[bool] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow()
        to_encode.update({"alg": algorithm})
        if "exp" not in payload and expires_delta:
            to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update(payload)
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
        return encoded_jwt

    # Decode a JWT into a payload
    def decode_jwt(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = jwt.decode(token, secret, algorithms=[algorithm])
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a JWE (JSON Web Encryption)
    def encode_jwe(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
        key_id: Optional[str] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        to_encode.update({"alg": algorithm})
        if "kid" in payload and key_id is not None:
            to_encode.update({"kid": key_id})
        to_encode.update(payload)
        encoded_jwe = algorithms.encode(to_encode, secret, algorithm=algorithm)
        return encoded_jwe

    # Decode a JWE into a payload
    def decode_jwe(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
        key_id: Optional[str] = None,
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = algorithms.decode(token, secret, algorithm=algorithm)
            if key_id is not None and "kid" in decoded_token:
                del decoded_token["kid"]
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a JWS (JSON Web Signature)
    def encode_jws(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
    ) -> str:
        to_encode: Dict[str, Any] = {}
        to_encode.update({"alg": algorithm})
        to_encode.update(payload)
        encoded_jws = algorithms.sign(to_encode, secret, algorithm=algorithm)
        return encoded_jws

    # Decode a JWS into a payload
    def decode_jws(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = algorithms.verify(token, secret, algorithm=algorithm)
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a compact JWS/JWE
    def encode_compact(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        if header is not None:
            to_encode.update(header)
        to_encode.update(payload)
        encoded_compact = algorithms.encode(to_encode, secret, algorithm=algorithm)
        return encoded_compact

    # Decode a compact JWS/JWE into a payload
    def decode_compact(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = algorithms.decode(token, secret, algorithm=algorithm)
            if header is not None and "alg" in header:
                del decoded_token["alg"]
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a JWK (JSON Web Key) compact representation
    def encode_jwk(
        self,
        key: Dict[str, Any],
        algorithm: str = "HS256",
        use: Optional[str] = None,
        key_ops: Optional[List[str]] = None,
        key_id: Optional[str] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        to_encode.update({"alg": algorithm})
        if use is not None:
            to_encode.update({"use": use})
        if key_ops is not None:
            to_encode.update({"key_ops": key_ops})
        if key_id is not None:
            to_encode.update({"kid": key_id})
        to_encode.update(key)
        encoded_jwk = slip(to_encode)
        return encoded_jwk

    # Decode a JWK into a payload
    def decode_jwk(
        self,
        token: str,
        algorithm: str = "HS256",
        use: Optional[str] = None,
        key_ops: Optional[List[str]] = None,
        key_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            decoded_token: Dict[str, Any] = slip(jwt.decode(token, algorithm=algorithm))
            if key_id is not None and "kid" in decoded_token:
                del decoded_token["kid"]
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a JWE with a compact representation
    def encode_compact_jwe(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
        key_id: Optional[str] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        if header is not None:
            to_encode.update(header)
        to_encode.update(payload)
        encoded_compact_jwe = algorithms.encode(to_encode, secret, algorithm=algorithm)
        return encoded_compact_jwe

    # Decode a compact JWE into a payload
    def decode_compact_jwe(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
        key_id: Optional[str] = None,
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = algorithms.decode(token, secret, algorithm=algorithm)
            if key_id is not None and "kid" in decoded_token:
                del decoded_token["kid"]
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None

    # Encode a payload into a JWS with a compact representation
    def encode_compact_jws(
        self,
        payload: TokenPayload,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
    ) -> str:
        to_encode: Dict[str, Any] = {}
        if header is not None:
            to_encode.update(header)
        to_encode.update(payload)
        encoded_compact_jws = algorithms.encode(to_encode, secret, algorithm=algorithm)
        return encoded_compact_jws

    # Decode a compact JWS into a payload
    def decode_compact_jws(
        self,
        token: str,
        secret: str,
        algorithm: str = "HS256",
        header: Optional[Dict[str, Any]] = None,
    ) -> Optional[TokenPayload]:
        try:
            decoded_token: Dict[str, Any] = algorithms.decode(token, secret, algorithm=algorithm)
            if header is not None and "alg" in header:
                del decoded_token["alg"]
            return decoded_token
        except JWTError as e:
            print(f"Invalid token: {e}")
            return None