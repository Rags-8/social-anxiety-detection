import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'social_anxiety.db')

def get_connection():
    """Get a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_text TEXT NOT NULL,
                anxiety_level VARCHAR(20) NOT NULL,
                sentiment_score FLOAT NOT NULL,
                suggestions TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("SQLite Database initialized successfully.")
        conn.close()
        return True
    except Exception as e:
        print(f"Warning: Could not connect/init database: {e}")
        return False
