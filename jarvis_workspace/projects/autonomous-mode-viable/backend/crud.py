from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional

app = FastAPI()

# Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] 
    email: Optional[EmailStr]
    password: Optional[str]

class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str

class UserProfile(BaseModel):
    user_id: int
    bio: Optional[str] = Field(None, min_length=1, max_length=300)
    avatar_url: Optional[str] = Field(None, min_length=5, max_length=500)

# Database
fake_db = {
    "users": [],
    "user_profiles": []
}

async def get_user(id: int) -> UserInDB:
    for user in fake_db["users"]:
        if user.id == id:
            return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

async def get_profile(user_id: int) -> UserProfile:
    for profile in fake_db["user_profiles"]:
        if profile.user_id == user_id:
            return profile
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

# Routes/Logic
@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate):
    existing_user = next((u for u in fake_db["users"] if u.username == user.username), None) 
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    new_user = UserInDB(id=len(fake_db["users"]) + 1, username=user.username, email=user.email, hashed_password=...)
    fake_db["users"].append(new_user)
    return new_user

@app.get("/users/{id}", response_model=UserInDB)
async def get_user_by_id(id: int):
    user = await get_user(id)
    return user

@app.put("/users/{id}", response_model=UserInDB)
async def update_user(id: int, updated_user: UserUpdate):
    user = await get_user(id)  
    for key in ['username', 'email']:
        if getattr(updated_user, key) is not None:
            setattr(user, key, getattr(updated_user, key))
    user.hashed_password = ...
    return user

@app.delete("/users/{id}")
async def delete_user(id: int):
    user = await get_user(id)
    fake_db["users"].remove(user)
    return {"detail": "User deleted"}

@app.post("/profiles/", response_model=UserProfile)
async def create_profile(profile: UserProfile, user_id: int = Depends(get_user)):
    existing_profile = next((p for p in fake_db["user_profiles"] if p.user_id == user_id), None)
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")
    
    new_profile = UserProfile(user_id=user_id, bio=profile.bio, avatar_url=profile.avatar_url) 
    fake_db["user_profiles"].append(new_profile)
    return new_profile

@app.get("/profiles/{user_id}", response_model=UserProfile)
async def get_profile_by_user_id(user_id: int):
    profile = await get_profile(user_id)
    return profile

@app.put("/profiles/{user_id}", response_model=UserProfile)
async def update_profile(user_id: int, updated_profile: UserProfile):
    existing_profile = await get_profile(user_id)
    for key in ['bio', 'avatar_url']:
        if getattr(updated_profile, key) is not None:
            setattr(existing_profile, key, getattr(updated_profile, key))
    return existing_profile

@app.delete("/profiles/{user_id}")
async def delete_profile(user_id: int):
    profile = await get_profile(user_id)
    fake_db["user_profiles"].remove(profile)
    return {"detail": "Profile deleted"}

# Error Handlers
@app.exception_handler(HTTPException)  
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )