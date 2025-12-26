from typing import Any, Callable, Dict, List, Optional, Union

import jwt
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

class JoseError(Exception):
    pass

def verify_jwt(
    token: str,
    public_key: str,
    algorithms: List[str] = ["RS256"],
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    try:
        return jwt.decode(token, public_key, algorithms=algorithms, options=options)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

def sign_jwt(
    payload: Union[BaseModel, Dict[str, Any]],
    private_key: str,
    algorithms: List[str] = ["RS256"],
    options: Optional[Dict[str, Any]] = None,
) -> str:
    if isinstance(payload, BaseModel):
        payload_dict = payload.dict()
    else:
        payload_dict = payload

    try:
        return jwt.encode(payload_dict, private_key, algorithms=algorithms, options=options)
    except Exception as e:
        raise JoseError(f"Failed to sign JWT: {str(e)}")