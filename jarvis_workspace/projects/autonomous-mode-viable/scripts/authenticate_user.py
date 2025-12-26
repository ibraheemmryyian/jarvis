from .databaseconnection import get_db
from .databaserecord import get_user_by_username

async def authenticate_user(username: str, password: str):
    db = next(get_db())
    user = await get_user_by_username(db=db, username=username)
    if not user:
        return False
    hashed_password = user.password
    if not verify_password.verify_password(password, hashed_password):
        return False
    return user