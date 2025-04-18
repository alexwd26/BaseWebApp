import sqlite3

def get_db_connection():
    # Replace with your actual database credentials
    db_path = 'your_database.db'  # Make sure this exists
    conn = sqlite3.connect(db_path)
    return conn