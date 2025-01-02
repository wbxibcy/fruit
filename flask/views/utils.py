import sqlite3

db_file = 'fruit_data.db'

def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn