from sqlalchemy import DateTime, Integer, String, ForeignKey
from .databaseconnection import Base

from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

    def __repr__(self):
        return f"<User {self.username}>"

# Add other models here