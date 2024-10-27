#%%
import json
import pandas as pd
from datetime import datetime, timedelta, time
import pytz

def load_historical_data():
    with open('data/updated_historical_data.json', 'r') as f:
        return json.load(f)

def parse_date(date_str):
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    try:
        # Try parsing as full datetime
        dt = pd.to_datetime(date_str)
        if dt.tzinfo is None:
            # If the parsed datetime is naive, assume it's in Amsterdam time
            dt = amsterdam_tz.localize(dt)
        return dt.astimezone(amsterdam_tz)
    except ValueError:
        try:
            # Try parsing as date only
            dt = pd.to_datetime(date_str, format='%Y-%m-%d')
            # Add default time (00:00:00) and set timezone
            return amsterdam_tz.localize(datetime.combine(dt.date(), time.min))
        except ValueError:
            # If still fails, return NaT
            return pd.NaT
    
    # Ensure timezone is set to Amsterdam
    return dt.astimezone(amsterdam_tz)

def prepare_data_for_supabase(historical_data):
    # Convert to DataFrame
    df = pd.DataFrame(historical_data)
    
    # Debugging: Print the first few rows of the date columns
    print("First few rows of date columns before conversion:")
    print(df[['date', 'start', 'end']].head())
    print(df[['date', 'start', 'end']].dtypes)

    # Convert date strings to datetime objects while preserving the timezone
    for col in ['date', 'start', 'end']:
        df[col] = df[col].apply(parse_date)
    
    # Debugging: Print the first few rows of the date columns after conversion
    print("\nFirst few rows of date columns after conversion:")
    print(df[['date', 'start', 'end']].head())
    print(df[['date', 'start', 'end']].dtypes)

    # Calculate duration in minutes, handling potential NaT values
    df['duration'] = (df['end'] - df['start']).dt.total_seconds().div(60).fillna(0)
    
    # Ensure all required columns are present
    required_columns = ['id', 'date', 'start', 'end', 'summary', 'calendar_name', 'description', 'deleted', 'value', 'duration']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Fill NaN values
    df['deleted'] = df['deleted'].fillna(False)
    df['value'] = df['value'].fillna(1)
    df['description'] = df['description'].fillna('')
    
    # Set value to 0.5 for fitness calendar events with 'rest' in the summary
    df.loc[(df['calendar_name'] == 'fitness') & (df['summary'].str.lower().str.contains('rest', na=False)), 'value'] = 0.5

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


# %%

# %%