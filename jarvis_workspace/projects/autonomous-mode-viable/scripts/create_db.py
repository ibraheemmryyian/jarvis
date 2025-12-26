# Implement database creation function
import sqlite3

def create_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connection established. Database file 'pythonsite.db' created.")
    except Error as e:
        print(e)