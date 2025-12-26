from sqlalchemy.ext.declarative import as_declarative, declared_attr

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id: int
    
    class Config:
        orm_mode = True
        
class Item(Base):
    name: str