import datetime
import os.path
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]
from googleapiclient.errors import HttpError  # type: ignore[import]

# If modifying these scopes, delete the token file.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

    def create_event(
        self,
        summary: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str = "",
        location: str = "",
        attendees: Optional[List[Dict[str, str]]] = None,
        calendar_id: str = "primary",
        timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Create a new event in the calendar.

        Args:
            summary: Title of the event
            start_time: Start time of the event
            end_time: End time of the event
            description: Description of the event
            location: Location of the event
            attendees: List of attendees, each a dict with at least 'email' key
            calendar_id: Calendar ID to add event to (default: primary)
            timezone: Timezone for the event times

        Returns:
            Created event object
        """
        if not self.service:
            self.authenticate()

        if attendees is None:
            attendees = []

        event_body: Dict[str, Any] = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
        }

        if attendees:
            event_body["attendees"] = attendees.copy()

        try:
            event = self.service.events().insert(calendarId=calendar_id, body=event_body).execute()

            return event
        except HttpError as error:
            raise Exception(f"An error occurred while creating the event: {error}")

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        calendar_id: str = "primary",
        timezone: str = "UTC",
    ) -> Dict[str, Any]:
        """
        Update an existing event in the calendar.

        Args:
            event_id: ID of the event to update
            summary: New title of the event
            start_time: New start time of the event
            end_time: New end time of the event
            description: New description of the event
            location: New location of the event
            attendees: New list of attendees, each a dict with at least 'email' key
            calendar_id: Calendar ID the event belongs to (default: primary)
            timezone: Timezone for the event times

        Returns:
            Updated event object
        """
        if not self.service:
            self.authenticate()

        # First get the existing event
        try:
            event: Dict[str, Any] = (
                self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )

            # Update fields if provided
            if summary is not None:
                event["summary"] = summary

            if description is not None:
                event["description"] = description

            if location is not None:
                event["location"] = location

            if start_time is not None:
                event["start"] = {
                    "dateTime": start_time.isoformat(),
                    "timeZone": timezone,
                }

            if end_time is not None:
                event["end"] = {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone,
                }

            if attendees is not None:
                event["attendees"] = attendees.copy()

            # Update the event
            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            return updated_event

        except HttpError as error:
            raise Exception(f"An error occurred while updating the event: {error}")

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        """
        Delete an event from the calendar.

        Args:
            event_id: ID of the event to delete
            calendar_id: Calendar ID the event belongs to (default: primary)

        Returns:
            True if successful
        """
        if not self.service:
            self.authenticate()

        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

            return True

        except HttpError as error:
            raise Exception(f"An error occurred while deleting the event: {error}")
