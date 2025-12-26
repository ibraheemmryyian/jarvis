import sqlite3

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

def create_database():
    conn = sqlite3.connect(SQLALCHEMY_DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, description TEXT)")

    conn.commit()

def create_db_connection():
    return sqlite3.connect(SQLALCHEMY_DATABASE_URL)