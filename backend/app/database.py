import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Get a new PostgreSQL connection with a timeout."""
    return psycopg2.connect(DATABASE_URL, connect_timeout=3)

def init_db():
    """Create the conversations table if it doesn't exist.
    Returns True on success, False on failure (so startup is non-fatal).
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_text TEXT NOT NULL,
                    anxiety_level VARCHAR(20) NOT NULL,
                    sentiment_score FLOAT NOT NULL,
                    suggestions TEXT[] NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()
        print("Database initialized successfully.")
        conn.close()
        return True
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("The app will still work for analysis, but history will not be saved.")
        return False
