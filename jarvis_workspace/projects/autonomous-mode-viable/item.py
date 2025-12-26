from sqlalchemy import Column, Integer, String
from .databaseconnection import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    def __repr__(self):
        return f"<Item {self.id} - {self.name}>"