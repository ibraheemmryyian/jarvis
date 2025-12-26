from .database import get_db

def get_item(item_id: int, db: Session = Depends(get_db)):
    return db.query(models.Item).filter(models.Item.id == item_id).first()