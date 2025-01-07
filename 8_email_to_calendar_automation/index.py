import re
import base64
from uuid import uuid4
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
from googleapiclient.errors import HttpError
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Scopes for Gmail and Google Calendar
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/gmail.send']

timeZone = 'Asia/Kolkata'
default_meeting_duration=1

def authenticate_google_api():
    """Authenticate and return a service object for Google APIs."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds

def get_latest_email(service):
    """Fetch the latest email containing meeting details."""
    # search email subject with given query to find the most appropriate emails
    results = service.users().messages().list(userId='me', q='subject:please plan a meeting').execute()
    messages = results.get('messages', [])
    if not messages:
        print("No new meeting emails.")
        return None, None
    
    msg_id = messages[0]['id']
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = msg['payload']
    headers = payload['headers']
    
    sender = None
    # find the sender from headers having 'From' tag
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
            break
    
    if not sender:
        print("Could not find sender email.")
        return None, None
    
    # Check for the email body in different locations
    if 'data' in payload['body']:
        # If the data is directly in the body
        email_body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    else:
        # If the data is in the parts of the payload
        parts = payload.get('parts', [])
        for part in parts:
            if part['mimeType'] == 'text/plain':  # Look for plain text content
                email_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
        else:
            print("No plain text content found.")
            return None, None
    
    return sender, email_body

def parse_email_for_meeting_details(email_body):
    """Extract meeting date, time, and other details from email body."""
    # regular expression for finding the date and time of meeting from email body
    pattern = r"please plan a meeting on (\d{4}-\d{2}-\d{2}) at (\d{1,2}:\d{2} (?:AM|PM))"
    # case insensitive search
    match = re.search(pattern, email_body, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return None, None

def schedule_meeting(service, sender, date, time):
    """Schedule a meeting in Google Calendar with India time zone and 1-hour duration."""
    # Fetch the calendar details to get the user's email address
    calendar = service.calendarList().get(calendarId='primary').execute()
    organizer_email = calendar['id']
    
    # Parse the date and time in 12-hour format (e.g., '03:00 PM') and convert to 24-hour format
    start_time_obj = datetime.strptime(f"{date} {time}", "%Y-%m-%d %I:%M %p")
    
    # Convert start time to ISO 8601 format (Google Calendar expects this format)
    start_time = start_time_obj.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Calculate the end time (1 hour after start time)
    end_time_obj = start_time_obj + timedelta(hours=default_meeting_duration)
    end_time = end_time_obj.strftime("%Y-%m-%dT%H:%M:%S")
    # this contain all details about the calendar invite along with gmeet specs 
    event = {
        'summary': 'Scheduled Automatic Meeting',
        'start': {'dateTime': start_time, 'timeZone': timeZone},
        'end': {'dateTime': end_time, 'timeZone': timeZone},
        'attendees': [{'email': sender}, {'email': organizer_email, 'responseStatus': 'accepted'}],
        'conferenceData': {
            'createRequest': {
                'requestId': f"{uuid4()}",  # Can be a unique value for each request
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'status': {'statusCode': 'success'}
            }
        }
    }
    event = service.events().insert(calendarId='primary', body=event,conferenceDataVersion=1).execute()
    # Get the Google Meet link from the event response
    google_meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
    return google_meet_link

def send_notification(service, recipient, meeting_link):
    """Send a notification email to the sender."""
    message = EmailMessage()
    message.set_content(f"Your meeting has been scheduled. Join here: {meeting_link}")
    message['To'] = recipient
    message['Subject'] = "Automatic Meeting Scheduled Notification"
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

def main():
    creds = authenticate_google_api()
    
    
    try:
        # Gmail Service
        gmail_service = build('gmail', 'v1', credentials=creds)
        sender, email_body = get_latest_email(gmail_service)
        
        if not email_body:
            print("No email body to process.")
            return
        
        date, time = parse_email_for_meeting_details(email_body)
        if not date or not time:
            print("Meeting details not found in email.")
            return
    
        # Calendar Service
        calendar_service = build('calendar', 'v3', credentials=creds)
        meeting_link = schedule_meeting(calendar_service, sender, date, time)
        
        # Send Notification
        send_notification(gmail_service, sender, meeting_link)
        print("Meeting scheduled and notification sent.")    
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
