"""
Tests for the Google Calendar Tool.

These tests verify the functionality of the GoogleCalendarTool class
without making actual API calls.
"""

import datetime
import pytest
from unittest.mock import MagicMock, patch

from googleapiclient.errors import HttpError  # type: ignore[import]

from naomi_core.tools.calendar.g_cal_tool import GoogleCalendarTool


def test_get_upcoming_events(mock_cal_tool, mock_service, mock_events):
    mock_service.events.return_value.list.return_value.execute.return_value = {
        "items": mock_events.copy()
    }

    assert mock_events == mock_cal_tool.get_upcoming_events(max_results=10, calendar_id="other")

    # Verify the service was called with the correct parameters
    mock_service.events.return_value.list.assert_called_once()
    call_kwargs = mock_service.events.return_value.list.call_args[1]
    assert call_kwargs["calendarId"] == "other"
    assert call_kwargs["maxResults"] == 10
    assert call_kwargs["singleEvents"] is True
    assert call_kwargs["orderBy"] == "startTime"


def test_get_upcoming_events_error(mock_cal_tool, mock_service):
    """Test error handling when getting upcoming events."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=404), content=b'{"error": "Calendar not found"}')
    mock_service.events.return_value.list.return_value.execute.side_effect = http_error

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.get_upcoming_events(calendar_id="nonexistent")

    assert "An error occurred while fetching events" in str(exc_info.value)
    assert "404" in str(exc_info.value) or "Calendar not found" in str(exc_info.value)


def test_get_calendar_list(mock_cal_tool, mock_service, mock_calendars):
    """Test getting calendar list."""
    expected_calendars = mock_calendars.copy()
    mock_service.calendarList.return_value.list.return_value.execute.return_value = {
        "items": expected_calendars
    }

    result = mock_cal_tool.get_calendar_list()

    assert result == expected_calendars
    assert result is not mock_calendars
    mock_service.calendarList.return_value.list.assert_called_once()


def test_get_calendar_list_error(mock_cal_tool, mock_service):
    """Test error handling when getting calendar list."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=401), content=b'{"error": "Unauthorized"}')
    mock_service.calendarList.return_value.list.return_value.execute.side_effect = http_error

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.get_calendar_list()

    assert "An error occurred while fetching calendars" in str(exc_info.value)
    assert "401" in str(exc_info.value) or "Unauthorized" in str(exc_info.value)


def test_get_event_details(mock_cal_tool, mock_service, mock_event_details):
    """Test getting event details."""
    expected_details = mock_event_details.copy()
    mock_service.events.return_value.get.return_value.execute.return_value = expected_details

    result = mock_cal_tool.get_event_details(event_id="event1", calendar_id="primary")

    assert result == expected_details
    assert result is not mock_event_details

    mock_service.events.return_value.get.assert_called_once_with(
        calendarId="primary", eventId="event1"
    )


def test_get_event_details_error(mock_cal_tool, mock_service):
    """Test error handling when getting event details."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=404), content=b'{"error": "Event not found"}')
    mock_service.events.return_value.get.return_value.execute.side_effect = http_error

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.get_event_details(event_id="nonexistent")

    assert "An error occurred while fetching event details" in str(exc_info.value)
    assert "404" in str(exc_info.value) or "Event not found" in str(exc_info.value)


def test_get_events_by_date_range(mock_cal_tool, mock_service, mock_events):
    """Test getting events by date range."""
    expected_events = mock_events.copy()
    mock_service.events.return_value.list.return_value.execute.return_value = {
        "items": expected_events
    }

    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 1, 31)

    result = mock_cal_tool.get_events_by_date_range(
        start_date=start_date,
        end_date=end_date,
        calendar_id="primary",
        max_results=100,
    )

    assert result == expected_events
    assert result is not mock_events

    mock_service.events.return_value.list.assert_called_once()
    call_kwargs = mock_service.events.return_value.list.call_args[1]
    assert call_kwargs["calendarId"] == "primary"
    assert call_kwargs["timeMin"] == "2025-01-01T00:00:00Z"
    assert call_kwargs["timeMax"] == "2025-01-31T00:00:00Z"
    assert call_kwargs["maxResults"] == 100


def test_get_events_by_date_range_error(mock_cal_tool, mock_service):
    """Test error handling when getting events by date range."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=400), content=b'{"error": "Invalid date range"}')
    mock_service.events.return_value.list.return_value.execute.side_effect = http_error

    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 1, 31)

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.get_events_by_date_range(start_date=start_date, end_date=end_date)

    assert "An error occurred while fetching events" in str(exc_info.value)
    assert "400" in str(exc_info.value) or "Invalid date range" in str(exc_info.value)


def test_format_event_time(mock_cal_tool):
    """Test formatting event time."""
    # Test event with dateTime
    event_with_datetime = {"start": {"dateTime": "2025-01-01T10:00:00Z"}}
    assert "2025-01-01T10:00:00Z" == mock_cal_tool.format_event_time(event_with_datetime)

    # Test event with date
    event_with_date = {"start": {"date": "2025-01-01"}}
    assert "2025-01-01" == mock_cal_tool.format_event_time(event_with_date)

    # Test event with both dateTime and date (dateTime should take precedence)
    event_with_both = {"start": {"dateTime": "2025-01-01T10:00:00Z", "date": "2025-01-01"}}
    assert "2025-01-01T10:00:00Z" == mock_cal_tool.format_event_time(event_with_both)


def test_create_event(mock_cal_tool, mock_service, mock_created_event, sample_datetime):
    """Test creating an event."""
    mock_service.events.return_value.insert.return_value.execute.return_value = mock_created_event

    start_time = sample_datetime
    end_time = datetime.datetime(2025, 1, 1, 11, 0, 0)
    attendees = [{"email": "test@example.com"}]

    result = mock_cal_tool.create_event(
        summary="Test Event",
        start_time=start_time,
        end_time=end_time,
        description="Test Description",
        location="Test Location",
        attendees=attendees,
        calendar_id="primary",
        timezone="UTC",
    )

    assert mock_created_event == result

    mock_service.events.return_value.insert.assert_called_once()
    call_kwargs = mock_service.events.return_value.insert.call_args[1]
    assert call_kwargs["calendarId"] == "primary"

    body = call_kwargs["body"]
    assert body["summary"] == "Test Event"
    assert body["description"] == "Test Description"
    assert body["location"] == "Test Location"
    assert body["start"]["dateTime"] == start_time.isoformat()
    assert body["end"]["dateTime"] == end_time.isoformat()
    assert body["attendees"] == attendees
    assert body["start"]["timeZone"] == "UTC"
    assert body["end"]["timeZone"] == "UTC"


def test_create_event_without_attendees(
    mock_cal_tool, mock_service, mock_created_event, sample_datetime
):
    """Test creating an event without attendees."""
    mock_service.events.return_value.insert.return_value.execute.return_value = mock_created_event

    start_time = sample_datetime
    end_time = datetime.datetime(2025, 1, 1, 11, 0, 0)

    mock_cal_tool.create_event(
        summary="Test Event",
        start_time=start_time,
        end_time=end_time,
        calendar_id="primary",
    )

    mock_service.events.return_value.insert.assert_called_once()
    call_kwargs = mock_service.events.return_value.insert.call_args[1]
    body = call_kwargs["body"]

    # Ensure attendees is not in the body
    assert "attendees" not in body


def test_create_event_error(mock_cal_tool, mock_service, sample_datetime):
    """Test error handling when creating an event."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=400), content=b'{"error": "Invalid event data"}')
    mock_service.events.return_value.insert.return_value.execute.side_effect = http_error

    start_time = sample_datetime
    end_time = datetime.datetime(2025, 1, 1, 11, 0, 0)

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.create_event(
            summary="Test Event",
            start_time=start_time,
            end_time=end_time,
        )

    assert "An error occurred while creating the event" in str(exc_info.value)
    assert "400" in str(exc_info.value) or "Invalid event data" in str(exc_info.value)


def test_update_event(mock_cal_tool, mock_service, mock_original_event, mock_updated_event):
    """Test updating an event."""
    mock_service.events.return_value.get.return_value.execute.return_value = mock_original_event
    mock_service.events.return_value.update.return_value.execute.return_value = mock_updated_event

    result = mock_cal_tool.update_event(
        event_id="event_id",
        summary="Updated Event",
        description="Updated Description",
        calendar_id="primary",
    )

    assert mock_updated_event == result

    mock_service.events.return_value.get.assert_called_once_with(
        calendarId="primary", eventId="event_id"
    )

    mock_service.events.return_value.update.assert_called_once()
    call_kwargs = mock_service.events.return_value.update.call_args[1]
    assert call_kwargs["calendarId"] == "primary"
    assert call_kwargs["eventId"] == "event_id"

    body = call_kwargs["body"]
    assert body["summary"] == "Updated Event"
    assert body["description"] == "Updated Description"
    assert body["location"] == "Original Location"  # Unchanged


def test_update_event_with_times(
    mock_cal_tool, mock_service, mock_original_event, mock_updated_event, sample_datetime
):
    """Test updating an event's times."""
    mock_service.events.return_value.get.return_value.execute.return_value = mock_original_event
    mock_service.events.return_value.update.return_value.execute.return_value = mock_updated_event

    start_time = sample_datetime
    end_time = datetime.datetime(2025, 1, 1, 12, 0, 0)  # Changed to noon

    result = mock_cal_tool.update_event(
        event_id="event_id",
        start_time=start_time,
        end_time=end_time,
        timezone="America/New_York",  # Using different timezone
        calendar_id="primary",
    )

    assert mock_updated_event == result

    mock_service.events.return_value.update.assert_called_once()
    call_kwargs = mock_service.events.return_value.update.call_args[1]
    body = call_kwargs["body"]

    # Check the updated times
    assert body["start"]["dateTime"] == start_time.isoformat()
    assert body["end"]["dateTime"] == end_time.isoformat()
    assert body["start"]["timeZone"] == "America/New_York"
    assert body["end"]["timeZone"] == "America/New_York"


def test_update_event_with_attendees(
    mock_cal_tool, mock_service, mock_original_event, mock_updated_event
):
    """Test updating event attendees."""
    mock_service.events.return_value.get.return_value.execute.return_value = mock_original_event
    mock_service.events.return_value.update.return_value.execute.return_value = mock_updated_event

    new_attendees = [
        {"email": "user1@example.com"},
        {"email": "user2@example.com", "responseStatus": "accepted"},
    ]

    mock_cal_tool.update_event(
        event_id="event_id",
        attendees=new_attendees,
        calendar_id="primary",
    )

    mock_service.events.return_value.update.assert_called_once()
    call_kwargs = mock_service.events.return_value.update.call_args[1]
    body = call_kwargs["body"]

    # Check the updated attendees
    assert body["attendees"] == new_attendees


def test_update_event_error(mock_cal_tool, mock_service):
    """Test error handling when updating an event."""
    # Mock the HttpError exception during retrieval
    http_error = HttpError(resp=MagicMock(status=404), content=b'{"error": "Event not found"}')
    mock_service.events.return_value.get.return_value.execute.side_effect = http_error

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.update_event(
            event_id="nonexistent",
            summary="Updated Event",
        )

    assert "An error occurred while updating the event" in str(exc_info.value)
    assert "404" in str(exc_info.value) or "Event not found" in str(exc_info.value)


def test_delete_event(mock_cal_tool, mock_service):
    """Test deleting an event."""
    mock_service.events.return_value.delete.return_value.execute.return_value = None

    result = mock_cal_tool.delete_event(event_id="event_id", calendar_id="primary")

    assert result is True
    mock_service.events.return_value.delete.assert_called_once_with(
        calendarId="primary", eventId="event_id"
    )


def test_delete_event_error(mock_cal_tool, mock_service):
    """Test error handling when deleting an event."""
    # Mock the HttpError exception
    http_error = HttpError(resp=MagicMock(status=404), content=b'{"error": "Event not found"}')
    mock_service.events.return_value.delete.return_value.execute.side_effect = http_error

    # Test that the error is properly propagated
    with pytest.raises(Exception) as exc_info:
        mock_cal_tool.delete_event(event_id="nonexistent")

    assert "An error occurred while deleting the event" in str(exc_info.value)
    assert "404" in str(exc_info.value) or "Event not found" in str(exc_info.value)


@patch("naomi_core.tools.calendar.g_cal_tool.authenticate_google_api")
def test_authenticate(mock_authenticate_google_api, tmp_path):
    """Test authenticate method using the google_auth module."""
    # Setup
    credentials_path = str(tmp_path / "credentials.json")
    token_path = str(tmp_path / "token.json")

    # Write empty files
    with open(credentials_path, "w") as f:
        f.write("{}")
    with open(token_path, "w") as f:
        f.write("{}")

    # Setup mock
    mock_authenticate_google_api.return_value = "mock_service"

    # Create instance with real file paths
    tool = GoogleCalendarTool(credentials_path, token_path)

    tool.authenticate()

    # Assertions
    mock_authenticate_google_api.assert_called_once_with(
        credentials_path, token_path, "calendar", "v3", ["https://www.googleapis.com/auth/calendar"]
    )
    assert tool.service == "mock_service"
