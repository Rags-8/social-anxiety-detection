import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("VITE_SUPABASE_URL", "")
key: str = os.environ.get("VITE_SUPABASE_ANON_KEY", "")

supabase: Client | None = None

if not url or not key:
    print("Warning: VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY not found in environment variables. DB connection will fail.")
else:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
