import argparse
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]
from googleapiclient.errors import HttpError  # type: ignore[import]

# If modifying these scopes, delete the token file.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main(credentials_path: str, token_path: str):
    """
    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.

    Args:
        credentials_path: Path to the credentials JSON file
        token_path: Path to store/read the token file
    """
    creds = None
    # The token file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(token_path)), exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
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

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Calendar API Sanity Check")
    parser.add_argument("--credentials", help="Path to the credentials JSON file", required=True)
    parser.add_argument("--token", help="Path to store/read the token file", default="token.json")

    args = parser.parse_args()

    main(credentials_path=args.credentials, token_path=args.token)
