"""
Tests for the Google Calendar Tool.

These tests verify the functionality of the GoogleCalendarTool class
without making actual API calls.
"""

import datetime


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


def test_delete_event(mock_cal_tool, mock_service):
    """Test deleting an event."""
    mock_service.events.return_value.delete.return_value.execute.return_value = None

    result = mock_cal_tool.delete_event(event_id="event_id", calendar_id="primary")

    assert result is True
    mock_service.events.return_value.delete.assert_called_once_with(
        calendarId="primary", eventId="event_id"
    )


def test_format_event_time(mock_cal_tool):
    """Test formatting event time."""
    event_with_datetime = {"start": {"dateTime": "2025-01-01T10:00:00Z"}}
    assert "2025-01-01T10:00:00Z" == mock_cal_tool.format_event_time(event_with_datetime)

    event_with_date = {"start": {"date": "2025-01-01"}}
    assert "2025-01-01" == mock_cal_tool.format_event_time(event_with_date)
