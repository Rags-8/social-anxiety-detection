import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Use PostgreSQL (Supabase) in production via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Get a new PostgreSQL connection using DATABASE_URL."""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable not set.")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Create the conversations table if it doesn't exist."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_text TEXT NOT NULL,
                anxiety_level VARCHAR(20) NOT NULL,
                sentiment_score FLOAT NOT NULL,
                suggestions TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("PostgreSQL Database initialized successfully.")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Warning: Could not connect/init database: {e}")
        return False
