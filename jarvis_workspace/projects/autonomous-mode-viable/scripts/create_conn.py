# Implement database connection functions here
import sqlite3

def create_conn():
    conn = None
    try:
        conn = sqlite3.connect('mydatabase.db')
    except Error as e:
        print(e)
    return conn