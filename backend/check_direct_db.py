import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_\backend\.env"
load_dotenv(env_path)

db_url = os.environ.get("DATABASE_URL")

print(f"Connecting to: {db_url}")

if not db_url:
    print("DATABASE_URL missing!")
else:
    try:
        conn = psycopg2.connect(db_url)
        print("Connected directly to Postgres!")
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM conversations;")
        count = cur.fetchone()[0]
        print(f"Data found: {count} rows")
        
        cur.execute("SELECT * FROM conversations LIMIT 5;")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
