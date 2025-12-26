@router.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = await database_record.get_by_id(Item, item_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item