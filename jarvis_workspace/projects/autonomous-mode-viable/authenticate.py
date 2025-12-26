from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username")
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")

    return user