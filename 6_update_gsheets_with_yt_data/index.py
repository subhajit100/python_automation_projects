import os
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv()

YOUTUB_API_KEY = os.getenv('YOUTBUE_API_KEY')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# The ID and range of the spreadsheet to edit.
SPREADSHEET_ID = "1hOAqrnjkwksty6eqzakyjrkpZEEQWAkMkRreBdiE5f0"
SAMPLE_RANGE_NAME = "DSAlist!A2"

# This method will update the google sheet with youtube links from dataList
def updateSheetsWithYtLinks(service, startCell, dataList):
# Prepare the requests for the batch update
    requests = []
    current_row = int(startCell[1:])  # Extract the starting row (e.g., from 'E6')

    for title, link in dataList:
        # Create a request to update the cell with a hyperlinked value
        requests.append({
        "updateCells": {
            "range": {
                "sheetId": 0,
                "startRowIndex": current_row - 1,
                "endRowIndex": current_row,
                "startColumnIndex": 4,  # Column 'E' corresponds to index 4 (0-based)
                "endColumnIndex": 5,
            },
            "rows": [{
                "values": [{
                    "userEnteredValue": {"formulaValue": f'=HYPERLINK("{link}", "{title}")'},
                    "userEnteredFormat": {
                        "textFormat": {
                            "fontSize": 14
                        }
                    }
                }]
            }],
            "fields": "userEnteredValue,userEnteredFormat.textFormat"
        }
    })
        current_row += 1  # Move to the next row

    # Batch update the requests
    body = {"requests": requests}
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("Cells updated successfully!")
    except HttpError as err:
        print(f"An error occurred: {err}")


# the below method will get the dataList from youtube api as a method parameter, and will update the tokens, and then gives access to google sheets.
def manageGoogleSheets(dataList):
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
       service = build("sheets", "v4", credentials=creds)
       updateSheetsWithYtLinks(service, 'E6', dataList)
    except HttpError as err:
       print(err)

# This method will call the youtube API and list the title and link to all the youtube videos for a give playlist (given playListId as method params)          
def getYoutubePlaylistData(playListId):
   # Build the YouTube API client
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUB_API_KEY)
    
    # List to store video details
    videos = []

    # Fetch playlist items
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playListId,
        maxResults=50  # Maximum results per request
    )

    while request:
        response = request.execute()
        for item in response["items"]:
            title = item["snippet"]["title"]
            # this is done as my format of title is a bit different having a | in between
            shrinkedTitle = title.split('|')[0].strip()
            video_id = item["snippet"]["resourceId"]["videoId"]
            if shrinkedTitle == 'Private video':
               continue
            videos.append((shrinkedTitle, f"https://www.youtube.com/watch?v={video_id}"))
        
        # Check if there is a next page
        request = youtube.playlistItems().list_next(request, response)
    
    return videos

     
# This is the main method which is called when the file runs.
def main():
  try:
    playListId = 'PLTAENWuWDOFZIksY0EyCIexy3pn9Tegd9'
    dataList = getYoutubePlaylistData(playListId)
    print(dataList)
    manageGoogleSheets(dataList)
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()