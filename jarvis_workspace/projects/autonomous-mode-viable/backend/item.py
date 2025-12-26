from sqlalchemy import DateTime, Column, Integer, String
from .base import Base
from datetime import datetime

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)