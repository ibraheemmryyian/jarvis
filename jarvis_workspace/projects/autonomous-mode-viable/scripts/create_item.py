@router.post("/items")
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    new_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        owner_id=item.owner_id,
    )
    await database_record.add(new_item)
    return {"message": "Item created successfully"}