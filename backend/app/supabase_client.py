import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables using absolute path
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

url: str = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY", "")

supabase: Client | None = None

if not url or not key:
    print(f"Warning: Supabase credentials not found at {env_path}. VITE_SUPABASE_URL: {bool(os.environ.get('VITE_SUPABASE_URL'))}, SUPABASE_URL: {bool(os.environ.get('SUPABASE_URL'))}")
else:
    try:
        supabase = create_client(url, key)
        print("Supabase client initialized.")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
