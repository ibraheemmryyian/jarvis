import sqlite3

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

def get_db_connection():
    conn = sqlite3.connect(SQLALCHEMY_DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn