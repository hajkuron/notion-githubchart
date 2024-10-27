import json
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np

def generate_ids(event):
    # Generate stable ID
    stable_properties = [
        event.get('summary', ''),
        event.get('description', ''),
        event.get('calendar_name', ''),
        event['start'].split('T')[0]
    ]
    print(stable_properties)
    stable_string = "|".join(str(prop) for prop in stable_properties)
    stable_id = hashlib.sha256(stable_string.encode()).hexdigest()

    # Generate version ID
    all_properties = [
        event.get('summary', ''),
        event.get('description', ''),
        event.get('calendar_name', ''),
        event['start'],
        event['end']
    ]
    version_string = "|".join(str(prop) for prop in all_properties)
    version_id = hashlib.sha256(version_string.encode()).hexdigest()

    return stable_id, version_id

def update_historical_data(historical_data):
    updated_data = []
    for event in historical_data:
        # Generate new IDs
        stable_id, version_id = generate_ids(event)
        
        # Update event with new fields
        updated_event = {
            **event,
            'id': stable_id,  # Replace old 'id' with new stable ID
            'version_id': version_id,
            'new_date': event['date'],
            'new_start': event['start'],
            'new_end': event['end'],
            'status': 'unchanged'  # Set all events to 'unchanged'
        }
        
        # Ensure description is an empty string if not present
        if 'description' not in updated_event:
            updated_event['description'] = ''
        
        # Remove 'deleted' field if it exists
        updated_event.pop('deleted', None)
        
        updated_data.append(updated_event)
    
    return updated_data

def main():
    # Load historical data
    with open('data/historical_data.json', 'r') as f:
        historical_data = json.load(f)
    
    print(f"Total events in original historical data: {len(historical_data)}")
    
    # Update historical data
    updated_data = update_historical_data(historical_data)
    
    print(f"Total events after updating: {len(updated_data)}")
    
    # Convert to DataFrame and remove duplicates
    df = pd.DataFrame(updated_data)
    df_deduped = df.drop_duplicates(subset='id', keep='first')
    
    # Replace NaN with empty string in 'description' column
    df_deduped['description'] = df_deduped['description'].fillna('')
    
    print(f"Total events after removing duplicates: {len(df_deduped)}")
    
    # Convert back to list of dictionaries
    final_data = df_deduped.to_dict('records')
    
    # Count events by status
    status_count = df_deduped['status'].value_counts().to_dict()
    
    print("Event status counts:")
    for status, count in status_count.items():
        print(f"{status}: {count}")
    
    # Save updated data
    with open('data/updated_historical_data.json', 'w') as f:
        json.dump(final_data, f, indent=2)

    print("Historical data has been updated and saved to 'data/updated_historical_data.json'")

if __name__ == "__main__":
    main()
