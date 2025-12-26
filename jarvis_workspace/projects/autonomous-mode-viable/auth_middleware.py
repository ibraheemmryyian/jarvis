from fastapi import FastAPI, Request
from .auth import authenticate_user

app = FastAPI()

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.headers.get("Authorization"):
        # Token validation logic here
        pass
    else:
        raise HTTPException(status_code=403, detail="Not authenticated")

    response = await call_next(request)
    return response