from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.post("/users")
async def create_user(user: User):
    # Rest of the code...