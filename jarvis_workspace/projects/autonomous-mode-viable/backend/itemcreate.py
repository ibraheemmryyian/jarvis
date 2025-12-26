from typing import List

from .base import Base


class ItemCreate(Base):
    name: str
    description: str = None

class ItemUpdate(Base):
    id: int
    name: str
    description: str = None

class UserCreate(Base):
    username: str
    password: str
    
class UserUpdate(Base):
    username: str
    password: str = None