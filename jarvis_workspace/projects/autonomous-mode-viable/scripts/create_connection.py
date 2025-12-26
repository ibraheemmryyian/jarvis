import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to the database {db_file}")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_data(conn, data):
    cur = conn.cursor()
    for key in data.keys():
        try:
            cur.execute('''INSERT INTO data (key, value) VALUES (?, ?)''', (key, str(data[key])))
        except sqlite3.IntegrityError as e:
            print(f"Failed to insert {key}: {e}")

def get_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM data")
    rows = cur.fetchall()
    return dict(rows)

def close_connection(conn):
    if conn:
        conn.close()