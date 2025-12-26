@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = await database_record.get_by_id(User, user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user