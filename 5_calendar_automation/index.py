from datetime import datetime, timezone, time, timedelta
from dotenv import load_dotenv
import os
from sys import argv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv()

# create a .env file and then store the calendar id which you want to play with, or you can use 'primary', if you want the default one 
codingCalendarId = os.getenv('CODING_TASKS_CALENDAR_ID') 

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get10EventsFromNow(service):
    # Call the Calendar API
    # below code is for finding upcoming 10 events
    now = datetime.now(timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId=codingCalendarId,
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])


def getTodaysEvents(service):
    # Define your timezone (e.g., UTC+5:30)
    my_timezone = timezone(timedelta(hours=5, minutes=30))

    # Today's date
    today = datetime.now(my_timezone).date()

    # Setting timeStart to today's starting time (00:00:00) with timezone
    timeStart = datetime.combine(today, time.min, tzinfo=my_timezone).isoformat()

    # Setting timeEnd to today's ending time (23:59:59.999999) with timezone
    timeEnd = datetime.combine(today, time.max, tzinfo=my_timezone).isoformat()
    
    events_result = (
        service.events()
        .list(
            calendarId=codingCalendarId,
            timeMin=timeStart,
            timeMax=timeEnd,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
     
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])   


def getTotalHoursForToday(service):
    # Define your timezone (e.g., UTC+5:30)
    my_timezone = timezone(timedelta(hours=5, minutes=30))

    # Today's date
    today = datetime.now(my_timezone).date()

    # Setting timeStart to today's starting time (00:00:00) with timezone
    timeStart = datetime.combine(today, time.min, tzinfo=my_timezone).isoformat()

    # Setting timeEnd to today's ending time (23:59:59.999999) with timezone
    timeEnd = datetime.combine(today, time.max, tzinfo=my_timezone).isoformat()

    events_result = (
        service.events()
        .list(
            calendarId=codingCalendarId,
            timeMin=timeStart,
            timeMax=timeEnd,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    totalTime = timedelta()
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      end =   event["end"].get("dateTime", event["end"].get("date"))
      # Parsing the datetime strings into datetime objects
      start_time = datetime.fromisoformat(start)
      end_time = datetime.fromisoformat(end)

      # Calculating the difference
      time_difference = end_time - start_time
      totalTime+= time_difference

    # Extract total hours, minutes, and seconds from total_time
    total_seconds = int(totalTime.total_seconds())
    total_hours, remainder = divmod(total_seconds, 3600)
    total_minutes, total_seconds = divmod(remainder, 60)
    print('total_hours: ', total_hours)       
    print('total_minutes: ', total_minutes)       
    print('total_seconds: ', total_seconds)     


def addEvent(service):
    # the below two variabes are passed from command line arguments
    description = argv[2] 
    durationHours = float(argv[3])

    # Define the timezone (IST, UTC+5:30)
    my_timezone = timezone(timedelta(hours=5, minutes=30))

    # Get the current time in IST
    start_time = datetime.now(my_timezone)

    # Calculate the end time by adding the duration
    end_time = start_time + timedelta(hours=durationHours)

    # Format the start and end times as ISO 8601 strings
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()

    # Create the event
    event = {
        "summary": description,
        "start": {
            "dateTime": start_time_iso,
            "timeZone": "Asia/Kolkata",  # Set the timezone to IST
        },
        "end": {
            "dateTime": end_time_iso,
            "timeZone": "Asia/Kolkata",  # Set the timezone to IST
        },
    }

    # Insert the event into the calendar
    events_result = service.events().insert(calendarId=codingCalendarId, body=event).execute()
    
  
def main():
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

  try:
    service = build("calendar", "v3", credentials=creds)
    
    methodToCall = argv[1]
    if methodToCall == 'get10':
      # this gives us the upcoming 10 events from now
      get10EventsFromNow(service)
    elif methodToCall == 'today':
      # this gives all the events of today
      getTodaysEvents(service) 
    elif methodToCall == 'geth':
      # this gives the total hours of today's meetings
      getTotalHoursForToday(service)
    elif methodToCall == 'add':
      # this lets us to add a new event to the calendar
      addEvent(service)     


  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()