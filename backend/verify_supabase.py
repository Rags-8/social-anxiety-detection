import os
import sys
from dotenv import load_dotenv

# Add the app directory to sys.path to import supabase_client
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from supabase_client import supabase
    print("Supabase client initialized successfully.")
    
    # Simple check to see if we can reach Supabase (e.g., list buckets or a dummy query)
    # We'll just check if the client object exists for now as a basic smoke test
    if supabase:
        print("Connection object created.")
    else:
        print("Failed to create connection object.")
        sys.exit(1)
        
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    sys.exit(1)
