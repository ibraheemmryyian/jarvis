from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class DatabaseRecord(Base):
    __tablename__ = 'records'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(String)

def create_connection():
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)
    return engine

def add_record(engine, data):
    conn = engine.connect()
    record = DatabaseRecord(data=data)
    conn.add(record)
    conn.commit()

def get_records(engine):
    conn = engine.connect()
    records = conn.query(DatabaseRecord).all()
    conn.close()
    return records