import sqlite3

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

def get_db():
    db = sqlite3.connect(SQLALCHEMY_DATABASE_URL)
    yield db
    db.close()