import os.path
from typing import Any, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
from googleapiclient.discovery import build  # type: ignore[import]

# Default scopes for Google Calendar
DEFAULT_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def authenticate_google_api(
    credentials_path: str,
    token_path: str,
    api_name: str,
    api_version: str,
    scopes: List[str],
) -> Any:
    """
    Authenticate with Google API and build a service.

    Args:
        credentials_path: Path to the credentials JSON file
        token_path: Path to store/read the token file
        api_name: Name of the Google API service (e.g., "calendar")
        api_version: Version of the API (e.g., "v3")
        scopes: List of OAuth scopes to request

    Returns:
        Built service for the specified API
    """

    creds = None
    # The token file stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                scopes,
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(token_path)), exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build(api_name, api_version, credentials=creds)
