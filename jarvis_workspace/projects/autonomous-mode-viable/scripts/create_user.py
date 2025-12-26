@router.post("/users")
async def create_user(user: UserCreate):
    hashed_password = password_hasher.hash(user.password)
    db_user = user_in_db(
        username=user.username,
        hashed_password=hashed_password,
        disabled=False,
    )
    await database_connection.add(db_user)
    return {"message": "User created successfully"}