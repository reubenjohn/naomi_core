import datetime
import os.path
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]
from googleapiclient.errors import HttpError  # type: ignore[import]

# If modifying these scopes, delete the token file.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarTool:
    """Tool for interacting with Google Calendar API."""

    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize the Google Calendar Tool.

        Args:
            credentials_path: Path to the credentials JSON file
            token_path: Path to store/read the token file
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service: Any = None

    def authenticate(self) -> None:
        """Authenticate with Google Calendar API."""
        creds = None
        # The token file stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at: {self.credentials_path}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.token_path)), exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)

    def get_upcoming_events(
        self, max_results: int = 10, calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events from the calendar.

        Args:
            max_results: Maximum number of events to return
            calendar_id: Calendar ID to fetch events from (default: primary)

        Returns:
            List of event objects
        """
        if not self.service:
            self.authenticate()

        try:
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])

        except HttpError as error:
            raise Exception(f"An error occurred while fetching events: {error}")

    def get_calendar_list(self) -> List[Dict[str, Any]]:
        """
        Get list of calendars available to the user.

        Returns:
            List of calendar objects
        """
        if not self.service:
            self.authenticate()

        try:
            calendars_result = self.service.calendarList().list().execute()
            return calendars_result.get("items", [])
        except HttpError as error:
            raise Exception(f"An error occurred while fetching calendars: {error}")

    def get_event_details(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Get details of a specific event.

        Args:
            event_id: ID of the event to fetch
            calendar_id: Calendar ID the event belongs to (default: primary)

        Returns:
            Event object
        """
        if not self.service:
            self.authenticate()

        try:
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            return event
        except HttpError as error:
            raise Exception(f"An error occurred while fetching event details: {error}")

    def get_events_by_date_range(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        calendar_id: str = "primary",
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get events within a specific date range.

        Args:
            start_date: Start date for the range
            end_date: End date for the range
            calendar_id: Calendar ID to fetch events from (default: primary)
            max_results: Maximum number of events to return

        Returns:
            List of event objects
        """
        if not self.service:
            self.authenticate()

        try:
            time_min = start_date.isoformat() + "Z"
            time_max = end_date.isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])

        except HttpError as error:
            raise Exception(f"An error occurred while fetching events: {error}")

    def format_event_time(self, event: Dict[str, Any]) -> str:
        """
        Format the event time for display.

        Args:
            event: Event object

        Returns:
            Formatted time string
        """
        start = event["start"].get("dateTime", event["start"].get("date"))
        return start
