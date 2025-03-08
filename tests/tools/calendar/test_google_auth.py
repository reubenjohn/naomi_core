import json
import os
from unittest.mock import MagicMock, patch

import pytest

from naomi_core.tools.calendar.google_auth import authenticate_google_api, DEFAULT_CALENDAR_SCOPES


@pytest.fixture
def credentials_file(tmp_path):
    """Create a credentials file."""
    credentials_file = tmp_path / "credentials.json"
    credentials_file.write_text("{}")
    return str(credentials_file)


@pytest.fixture
def token_file(tmp_path):
    """Create a token file with valid credentials."""
    token_file = tmp_path / "token.json"
    token_data = {
        "token": "valid_token",
        "refresh_token": "refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/calendar"],
        "expiry": "2099-01-01T00:00:00.000000Z",  # Far future to ensure token is valid
    }
    token_file.write_text(json.dumps(token_data))
    return str(token_file)


@pytest.fixture
def expired_token_file(tmp_path):
    """Create a token file with expired credentials."""
    token_file = tmp_path / "expired_token.json"
    token_data = {
        "token": "expired_token",
        "refresh_token": "refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/calendar"],
        "expiry": "2020-01-01T00:00:00.000000Z",  # Past date to ensure token is expired
    }
    token_file.write_text(json.dumps(token_data))
    return str(token_file)


@patch("naomi_core.tools.calendar.google_auth.Credentials")
@patch("naomi_core.tools.calendar.google_auth.build")
def test_authenticate_with_existing_token(
    mock_build, mock_credentials, credentials_file, token_file
):
    """Test authentication when token file exists."""
    # Setup
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_credentials.from_authorized_user_file.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Call the function
    result = authenticate_google_api(
        credentials_file, token_file, "calendar", "v3", DEFAULT_CALENDAR_SCOPES
    )

    # Verify the authentication flow
    mock_credentials.from_authorized_user_file.assert_called_once_with(
        token_file, DEFAULT_CALENDAR_SCOPES
    )
    mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
    assert result == mock_service


@patch("naomi_core.tools.calendar.google_auth.InstalledAppFlow")
@patch("naomi_core.tools.calendar.google_auth.build")
def test_authenticate_without_token(mock_build, mock_flow, credentials_file, tmp_path):
    """Test authentication when token file doesn't exist."""
    # Setup
    token_path = str(tmp_path / "new_token.json")

    mock_flow_instance = MagicMock()
    mock_flow.from_client_secrets_file.return_value = mock_flow_instance

    mock_creds = MagicMock()
    mock_creds.to_json.return_value = '{"token": "new_test_token"}'
    mock_flow_instance.run_local_server.return_value = mock_creds

    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Call the function - token file doesn't exist yet
    result = authenticate_google_api(
        credentials_file, token_path, "calendar", "v3", DEFAULT_CALENDAR_SCOPES
    )

    # Verify the authentication flow
    mock_flow.from_client_secrets_file.assert_called_once_with(
        credentials_file, DEFAULT_CALENDAR_SCOPES
    )
    mock_flow_instance.run_local_server.assert_called_once_with(port=0)
    mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
    assert result == mock_service

    # Verify the token file was created
    assert os.path.exists(token_path)
    with open(token_path, "r") as f:
        assert f.read() == '{"token": "new_test_token"}'


@patch("naomi_core.tools.calendar.google_auth.Credentials")
@patch("naomi_core.tools.calendar.google_auth.Request")
@patch("naomi_core.tools.calendar.google_auth.build")
def test_authenticate_with_expired_token(
    mock_build, mock_request, mock_credentials, credentials_file, expired_token_file
):
    """Test authentication when token is expired but can be refreshed."""
    # Setup
    mock_creds = MagicMock()
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = True
    mock_creds.to_json.return_value = '{"refreshed": "token"}'

    mock_credentials.from_authorized_user_file.return_value = mock_creds
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Call the function
    result = authenticate_google_api(
        credentials_file, expired_token_file, "calendar", "v3", DEFAULT_CALENDAR_SCOPES
    )

    # Verify the authentication flow
    mock_credentials.from_authorized_user_file.assert_called_once_with(
        expired_token_file, DEFAULT_CALENDAR_SCOPES
    )
    mock_creds.refresh.assert_called_once_with(mock_request())
    mock_build.assert_called_once_with("calendar", "v3", credentials=mock_creds)
    assert result == mock_service

    # Verify the token file was updated with refreshed token
    with open(expired_token_file, "r") as f:
        assert f.read() == '{"refreshed": "token"}'


@patch("naomi_core.tools.calendar.google_auth.Credentials")
@patch("naomi_core.tools.calendar.google_auth.build")
def test_authenticate_with_custom_scopes(
    mock_build, mock_credentials, credentials_file, token_file
):
    """Test authentication with custom scopes."""
    # Setup
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_credentials.from_authorized_user_file.return_value = mock_creds

    custom_scopes = ["https://www.googleapis.com/auth/calendar.readonly"]

    # Call with custom scopes
    authenticate_google_api(credentials_file, token_file, "calendar", "v3", scopes=custom_scopes)

    # Verify the scopes were passed correctly
    mock_credentials.from_authorized_user_file.assert_called_once_with(token_file, custom_scopes)


def test_missing_credentials_file(tmp_path):
    """Test exception raised when credentials file is missing."""
    # Setup
    nonexistent_credentials = str(tmp_path / "nonexistent_credentials.json")
    token_path = str(tmp_path / "token.json")

    # Ensure the file doesn't exist
    if os.path.exists(nonexistent_credentials):
        os.remove(nonexistent_credentials)

    # Call should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        authenticate_google_api(
            nonexistent_credentials, token_path, "calendar", "v3", DEFAULT_CALENDAR_SCOPES
        )


def test_unsupported_api_no_scopes():
    pass
