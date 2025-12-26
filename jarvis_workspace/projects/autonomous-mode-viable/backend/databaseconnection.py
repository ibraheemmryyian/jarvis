from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DatabaseConnection:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return sessionmaker(bind=self.engine)()


def create_database():
    db_url = "sqlite:///./test.db"
    conn = DatabaseConnection(db_url)
    Session = conn.get_session()
    
    class User(Base):
        __tablename__ = 'users'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        email = Column(String(120), unique=True)

    Base.metadata.create_all(bind=conn.engine)


if __name__ == "__main__":
    create_database()