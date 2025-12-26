from fastapi import FastAPI
from .auth import pwd_context

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

class Settings:
    # Add your other settings here
    pass