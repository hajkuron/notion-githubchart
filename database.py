import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file")
    
    return create_client(url, key)

def load_prepared_data(file_path: str):
    with open(file_path, 'r') as file:
        return json.load(file)

def sync_with_supabase(prepared_data):
    supabase = get_supabase_client()
    
    # Upsert data
    table_name = 'calendar_events'
    response = supabase.table(table_name).upsert(prepared_data).execute()
    
    if hasattr(response, 'error') and response.error:
        print(f"Error upserting data: {response.error}")
    else:
        print(f"Upserted {len(prepared_data)} events")
    
    print("Data upsert completed.")

if __name__ == "__main__":
    json_file_path = 'data/prepared_data_for_supabase.json'
    prepared_data = load_prepared_data(json_file_path)
    sync_with_supabase(prepared_data)
    print("Sync completed")
