"""
Fixtures for testing the Google Calendar Tool.
"""

import datetime
import pytest
from unittest.mock import MagicMock, patch

from naomi_core.tools.calendar.g_cal_tool import GoogleCalendarTool


@pytest.fixture
def mock_service():
    """Create a mock Google Calendar service."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_cal_tool(mock_service):
    """Create a mock GoogleCalendarTool with a mocked service."""
    with patch.object(GoogleCalendarTool, "authenticate"):
        tool = GoogleCalendarTool(
            credentials_path="mock_credentials.json", token_path="mock_token.json"
        )
        # Set the mocked service
        tool.service = mock_service
        yield tool


@pytest.fixture
def sample_datetime():
    """Create a sample datetime object."""
    return datetime.datetime(2025, 1, 1, 10, 0, 0)


@pytest.fixture
def mock_events():
    """Return mock events data."""
    return [
        {
            "id": "event1",
            "summary": "Test Event 1",
            "start": {"dateTime": "2025-01-01T10:00:00Z"},
            "end": {"dateTime": "2025-01-01T11:00:00Z"},
        },
        {
            "id": "event2",
            "summary": "Test Event 2",
            "start": {"dateTime": "2025-01-02T10:00:00Z"},
            "end": {"dateTime": "2025-01-02T11:00:00Z"},
        },
    ]


@pytest.fixture
def mock_calendars():
    """Return mock calendars data."""
    return [
        {
            "id": "calendar1",
            "summary": "Primary Calendar",
        },
        {
            "id": "calendar2",
            "summary": "Work Calendar",
        },
    ]


@pytest.fixture
def mock_event_details():
    """Return mock event details."""
    return {
        "id": "event1",
        "summary": "Test Event",
        "description": "Test Description",
        "location": "Test Location",
        "start": {"dateTime": "2025-01-01T10:00:00Z"},
        "end": {"dateTime": "2025-01-01T11:00:00Z"},
    }


@pytest.fixture
def mock_created_event():
    """Return mock created event data."""
    return {
        "id": "new_event_id",
        "summary": "Test Event",
        "description": "Test Description",
        "location": "Test Location",
        "start": {"dateTime": "2025-01-01T10:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-01T11:00:00Z", "timeZone": "UTC"},
        "attendees": [{"email": "test@example.com"}],
    }


@pytest.fixture
def mock_original_event():
    """Return mock original event data for update tests."""
    return {
        "id": "event_id",
        "summary": "Original Event",
        "description": "Original Description",
        "location": "Original Location",
        "start": {"dateTime": "2025-01-01T10:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-01T11:00:00Z", "timeZone": "UTC"},
    }


@pytest.fixture
def mock_updated_event():
    """Return mock updated event data."""
    return {
        "id": "event_id",
        "summary": "Updated Event",
        "description": "Updated Description",
        "location": "Original Location",  # Not updated
        "start": {"dateTime": "2025-01-01T10:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-01T11:00:00Z", "timeZone": "UTC"},
    }


@pytest.fixture
def sample_event():
    """Create a sample event object."""
    return {
        "id": "event123",
        "summary": "Sample Event",
        "description": "This is a sample event for testing",
        "location": "Virtual",
        "start": {"dateTime": "2025-01-01T10:00:00Z", "timeZone": "UTC"},
        "end": {"dateTime": "2025-01-01T11:00:00Z", "timeZone": "UTC"},
        "attendees": [{"email": "test@example.com"}],
        "status": "confirmed",
    }


@pytest.fixture
def sample_calendar():
    """Create a sample calendar object."""
    return {
        "id": "calendar123",
        "summary": "Test Calendar",
        "description": "Calendar for testing",
        "timeZone": "UTC",
        "accessRole": "owner",
    }
