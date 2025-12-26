import sqlite3

def connect(db_name):
    return sqlite3.connect(db_name)

def create_table(conn, table_name, columns):
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
    conn.commit()

def insert_data(conn, table_name, data):
    placeholders = ', '.join(['?' for _ in range(len(data))])
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    conn.execute(query, data)
    conn.commit()

def fetch_all(conn, table_name, columns=None, condition=None):
    cursor = conn.cursor()
    query = f"SELECT {'*, '.join(columns) if columns else '*'} FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
    return cursor.fetchall()

def update_data(conn, table_name, set_values, condition):
    query = f"UPDATE {table_name} SET {' = ?, '.join(set_values)}"
    if condition:
        query += f" WHERE {condition}"
    conn.execute(query, [value for value in set_values])
    conn.commit()

def delete_data(conn, table_name, condition):
    query = f"DELETE FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    conn.execute(query)
    conn.commit()