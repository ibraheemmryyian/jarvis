import sqlite3
from contextlib import closing

class SQLAlchemy:
    @staticmethod
    def get_connection():
        return sqlite3.connect('jarvis.db')

    @staticmethod
    def execute_query(query, params=None):
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            return result

    @staticmethod
    def fetch_one(query, params=None):
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row

    @staticmethod
    def fetch_all(query, params=None):
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows

    @staticmethod
    def execute_commit_insert(query, params=None):
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    @staticmethod
    def create_table(table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column[0]} {column[1]}' for column in columns])})"
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @staticmethod
    def insert_data(table_name, data):
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in range(len(data))])
        values = [value for value in data.values()]
        query = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(values))
            conn.commit()

    @staticmethod
    def update_data(table_name, set_values, conditions):
        set_clause = ', '.join([f"{key}=?" for key in set_values.keys()])
        where_clause = ' AND '.join([f"{condition[0]}='{condition[1]}'" for condition in conditions])
        placeholders = ['?'] * (len(set_values) + len(conditions))
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query, placeholders)
            conn.commit()

    @staticmethod
    def delete_data(table_name, conditions):
        where_clause = ' AND '.join([f"{condition[0]}='{condition[1]}'" for condition in conditions])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    @staticmethod
    def execute_function(function_name, params=None):
        with closing(SQLAlchemy.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.callproc(function_name, params)
            result = cursor.fetchall()
            conn.commit()
            return result