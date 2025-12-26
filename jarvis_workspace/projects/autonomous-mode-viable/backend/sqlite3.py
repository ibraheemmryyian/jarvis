import sqlite3

class SQLite3:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
    
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            print("Connected to SQLite database")
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
    
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            print("Query executed successfully")
        except Exception as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query, params=None):
        try:
            result = self.cursor.execute(query, params).fetchall()
            return result
        except Exception as e:
            print(f"Error fetching data: {e}")
    
    def close_connection(self):
        if self.conn is not None and self.conn.isopen():
            self.conn.close()
            print("SQLite connection closed")