import sqlite3

def connect_db():
    conn = sqlite3.connect("main.db")
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        task_name TEXT NOT NULL,
                        description TEXT,
                        status TEXT NOT NULL
                    )''')
    conn.commit()

def add_task(conn, task_name, description, status="Pending"):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task_name, description, status) VALUES (?, ?, ?)", (task_name, description, status))
    conn.commit()

def update_status(conn, task_id, new_status):
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()

def get_all_tasks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def get_task_by_id(conn, task_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    return row

def delete_task(conn, task_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()