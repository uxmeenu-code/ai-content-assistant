from googleapiclient.discovery import build
from google.auth import default

creds, _ = default()
service = build("calendar", "v3", credentials=creds)

events = service.events().list(calendarId="primary", maxResults=5).execute()

print(events)