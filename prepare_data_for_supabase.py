#%%
import json
import pandas as pd
from datetime import datetime, timedelta

def load_historical_data():
    with open('data/historical_data.json', 'r') as f:
        return json.load(f)

def prepare_data_for_supabase(historical_data):
    # Convert to DataFrame
    df = pd.DataFrame(historical_data)
    
    # Convert date strings to datetime objects
    df['date'] = pd.to_datetime(df['date'])
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    
    # Calculate duration in minutes
    df['duration'] = (df['end'] - df['start']).dt.total_seconds() / 60
    
    # Ensure all required columns are present
    required_columns = ['id', 'date', 'start', 'end', 'summary','calendar_name', 'description', 'deleted', 'value', 'duration']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Fill NaN values
    df['deleted'] = df['deleted'].fillna(False)
    df['value'] = df['value'].fillna(1)
    df['description'] = df['description'].fillna('')
    
    # Set value to 0.5 for fitness calendar events with 'rest' in the summary
    df.loc[(df['calendar_name'] == 'fitness') & (df['summary'].str.lower().str.contains('rest')), 'value'] = 0.5

    # Remove duplicates, keeping the first occurrence
    df = df.drop_duplicates(subset=['id'], keep='first')

    return df


def save_prepared_data(df):
    # Save to CSV for easy inspection
    df.to_csv('data/prepared_data_for_supabase.csv', index=False)
    
    # Save to JSON for pushing to Supabase
    df.to_json('data/prepared_data_for_supabase.json', orient='records', date_format='iso')

#%%
if __name__ == "__main__":
    historical_data = load_historical_data()
    prepared_df = prepare_data_for_supabase(historical_data)
    save_prepared_data(prepared_df)
    print("Data prepared and saved successfully.")
#%%
historical_data = load_historical_data()
prepared_df = prepare_data_for_supabase(historical_data)
    

# %%

# %%