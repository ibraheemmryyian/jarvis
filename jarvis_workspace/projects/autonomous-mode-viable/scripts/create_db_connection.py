# This file should handle the actual database connection and pooling
from sqlalchemy import create_engine, Engine
from databases.core import Database

DATABASE_URL = "sqlite:///./test.db"  # Update with your DB URL

engine = create_engine(DATABASE_URL)
TestDatabaseConnection = Database(DATABASE_URL)

def create_db_connection():
    return TestDatabaseConnection.connect()