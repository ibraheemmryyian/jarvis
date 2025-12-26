from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            auth = scope.get("headers", {}).get(b"authorization")
            if auth and auth.startswith(b"Bearar"):
                _, token = auth.decode().split(" ")
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    user_id: int = payload.get("user_id")
                    if user_id is not None:
                        scope["user_id"] = user_id
                except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                    raise HTTPException(status_code=401, detail="Invalid Token")
            else:
                raise HTTPException(status_code=403, detail="Not Authenticated")

        await self.app(scope, receive, send)