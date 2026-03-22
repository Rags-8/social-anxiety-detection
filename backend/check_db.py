import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
env_path = r"c:\Users\ragha\OneDrive\Desktop\Social_Anxiety_\backend\.env"
load_dotenv(env_path)

url = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL", "")
key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY", "")

print(f"URL: {url}")
print(f"Key length: {len(key)}")

if not url or not key:
    print("Credentials missing!")
else:
    try:
        supabase: Client = create_client(url, key)
        print("Supabase client initialized.")
        
        response = supabase.table("conversations").select("*").limit(5).execute()
        print(f"Data found: {len(response.data)} rows")
        for row in response.data:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
