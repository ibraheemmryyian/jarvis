import sqlite3

def create_connection():
    connection = sqlite3.connect("test.db")
    connection.row_factory = sqlite3.Row
    return connection