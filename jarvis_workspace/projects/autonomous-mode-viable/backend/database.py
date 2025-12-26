from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models, crud
from typing import List

router = APIRouter()

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(schemas.get_db)):
    item = crud.get_item(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item