import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "anxiety_predictions.db")

def get_connection():
    """Get a direct connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def init_db():
    """Initialize the SQLite database table."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                detected_words TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    finally:
        conn.close()
