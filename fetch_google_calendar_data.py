import os
import json
import hashlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_google_calendar_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_all_calendar_ids(service):
    calendar_list = service.calendarList().list().execute()
    # Print all calendar IDs and names for debugging
    for calendar in calendar_list['items']:
        print(f"Calendar ID: {calendar['id']}, Name: {calendar['summary']}")
    return [calendar['id'] for calendar in calendar_list['items']]

def get_calendar_events(service, calendar_id='primary', time_min=None, time_max=None, calendar_to_exclude=None):
    if not time_min:
        time_min = (datetime.utcnow() - datetime.timedelta(days=30)).isoformat() + 'Z'
    if not time_max:
        time_max = (datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'
    
    events_result = service.events().list(calendarId=calendar_id, timeMin=time_min,
                                          timeMax=time_max, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    # Get calendar name
    calendar = service.calendars().get(calendarId=calendar_id).execute()
    calendar_name = calendar['summary']
    
    # Add calendar name to each event and ensure each event has a summary
    filtered_events = []
    for event in events:
        if calendar_name != calendar_to_exclude:
            event['calendar_name'] = calendar_name
            if 'summary' not in event:
                event['summary'] = '(No title)'
            # Add description to the event, or '(No description)' if it's missing
            event['description'] = event.get('description', '(No description)')
            filtered_events.append(event)
    
    return filtered_events

def load_historical_data():
    try:
        with open('data/historical_data.json', 'r') as f:
            data = json.load(f)
            # Ensure all historical events have IDs
            for event in data:
                if 'id' not in event:
                    event['id'] = generate_id(event)
            return data
    except FileNotFoundError:
        return []

def save_historical_data(data):
    with open('data/historical_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def generate_id(event):
    # Create a unique ID based on the event's start time, summary, and calendar name
    if isinstance(event, dict):
        start_time = event.get('start', {})
        if isinstance(start_time, dict):
            start_time = start_time.get('dateTime', start_time.get('date', ''))
        summary = event.get('summary', '')
        calendar_name = event.get('calendar_name', '')
    else:
        # If event is not a dictionary, use it as is
        start_time = str(event)
        summary = ''
        calendar_name = ''
    
    id_string = f"{start_time}-{summary}-{calendar_name}"
    return hashlib.md5(id_string.encode()).hexdigest()

def compare_and_update_historical_data(new_events, historical_data):
    # Create a dictionary of new events for quick lookup
    new_event_dict = {event['id']: event for event in new_events}
    
    # Update historical data
    updated_historical_data = []
    for historical_event in historical_data:
        # Ensure historical event has an ID
        if 'id' not in historical_event:
            historical_event['id'] = generate_id(historical_event)
        
        if historical_event['id'] in new_event_dict:
            # Update existing event
            updated_event = new_event_dict.pop(historical_event['id'])
            updated_historical_data.append(updated_event)
        else:
            # Mark as deleted if it's not in new events
            historical_event['deleted'] = True
            updated_historical_data.append(historical_event)
    
    # Add any new events that weren't matched
    updated_historical_data.extend(new_event_dict.values())
    
    return updated_historical_data

def process_and_save_data():
    try:
        service = get_google_calendar_service()
        print("Successfully connected to Google Calendar.")
        
        # Get all calendar IDs
        calendar_ids = get_all_calendar_ids(service)
        print(f"Found {len(calendar_ids)} calendars.")
        
        # Set time range from September 1, 2024 until now
        time_min = datetime(2024, 9, 1).isoformat() + 'Z'
        time_max = datetime.utcnow().isoformat() + 'Z'
        
        calendars_to_exclude = [
            "University of Amsterdam - Personal timetable: 13597698@uva.nl",
            "VU Amsterdam - Personal timetable: Kuhar, J. (Jon)",
            "3eqkug64cc9rpbi0srd8mdoin01vl9l8@import.calendar.google.com",
            "24apf9qtnt0m4o0d0rsph9qibap9rfrm@import.calendar.google.com"
        ]

        # Dictionary to store events for each calendar
        calendar_events = {}

        for calendar_id in calendar_ids:
            # Get the calendar name before fetching events
            calendar = service.calendars().get(calendarId=calendar_id).execute()
            calendar_name = calendar['summary']
            
            # Skip calendars in the exclusion list
            if calendar_name in calendars_to_exclude or calendar_id in calendars_to_exclude:
                print(f"Skipping excluded calendar: {calendar_name}")
                continue

            events = get_calendar_events(service, calendar_id, time_min, time_max)
            if events:
                calendar_events[calendar_name] = events
                print(f"Fetched {len(events)} events from calendar: {calendar_name}")
            else:
                print(f"No events fetched from calendar: {calendar_name}")

        print(f"Fetched events from {len(calendar_events)} calendars.")

        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)

        # Load all historical data once before processing calendars
        all_historical_data = load_historical_data()

        # Process and save data for each calendar
        for calendar_name, events in calendar_events.items():
            processed_data = []
            for event in events:
                processed_event = {
                    "date": event['start'].get('dateTime', event['start'].get('date')),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "value": 0.5 if calendar_name == "Fitness" and "rest" in event.get('summary', '').lower() else 1,
                    "summary": event.get('summary', ''),
                    "description": event.get('description', ''),
                    "calendar_name": calendar_name
                }
                processed_event["id"] = generate_id(processed_event)
                processed_data.append(processed_event)

            # Filter historical data for the current calendar_name for comparison
            historical_data_for_calendar = [event for event in all_historical_data if event.get('calendar_name') == calendar_name]

            # Compare and update historical data for the current calendar
            updated_historical_data_for_calendar = compare_and_update_historical_data(processed_data, historical_data_for_calendar)

            # Update the overall historical data with the updated data for the current calendar
            all_historical_data = [event for event in all_historical_data if event.get('calendar_name') != calendar_name]
            all_historical_data.extend(updated_historical_data_for_calendar)

            # Create a valid filename from the calendar name
            filename = f"chart-data-{calendar_name.replace(' ', '_').replace(':', '').replace('@', '_')}.json"
            file_path = os.path.join('data', filename)

            # Write the processed data to the JSON file
            with open(file_path, 'w') as f:
                json.dump(processed_data, f, indent=2)

            print(f'Saved data for calendar "{calendar_name}" to {file_path}')

        # Save the updated historical data back to the file after processing all calendars
        save_historical_data(all_historical_data)

        print('Google Calendar data fetched and saved successfully')
    except Exception as error:
        print('Error processing Google Calendar data:', str(error))

if __name__ == '__main__':
    process_and_save_data()
