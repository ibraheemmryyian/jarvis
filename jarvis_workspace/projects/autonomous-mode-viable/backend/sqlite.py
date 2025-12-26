import sqlite3

class SQLite:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        column_str = ", ".join([f"{column} {datatype}" for column, datatype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name, data):
        column_names = list(data.keys())
        placeholders = ", ".join(["?" for _ in range(len(column_names))])
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()