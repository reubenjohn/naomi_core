#!/usr/bin/env python
import argparse
import datetime
import json
import sys
from typing import Any, Dict, List

from naomi_core.tools.calendar.g_cal_tool import GoogleCalendarTool


def display_events(events: List[Dict[str, Any]]) -> None:
    """
    Display events in a readable format.

    Args:
        events: List of event objects
    """
    if not events:
        print("No events found.")
        return

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{start} - {event.get('summary', 'No title')}")


def display_calendars(calendars: List[Dict[str, Any]]) -> None:
    """
    Display calendars in a readable format.

    Args:
        calendars: List of calendar objects
    """
    if not calendars:
        print("No calendars found.")
        return

    print("Available calendars:")
    for calendar in calendars:
        print(f"ID: {calendar['id']} - Name: {calendar.get('summary', 'No name')}")


def parse_date(date_str: str) -> datetime.datetime:
    """
    Parse date string into datetime object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        datetime object
    """
    try:
        year, month, day = map(int, date_str.split("-"))
        return datetime.datetime(year, month, day)
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Please use YYYY-MM-DD format.")
        sys.exit(1)


def parse_datetime(datetime_str: str) -> datetime.datetime:
    """
    Parse datetime string into datetime object.

    Args:
        datetime_str: Datetime string in YYYY-MM-DDTHH:MM format

    Returns:
        datetime object
    """
    try:
        # Split into date and time parts
        parts = datetime_str.split("T")
        if len(parts) != 2:
            raise ValueError("Invalid format")

        date_part, time_part = parts
        year, month, day = map(int, date_part.split("-"))
        hour, minute = map(int, time_part.split(":"))

        return datetime.datetime(year, month, day, hour, minute)
    except ValueError:
        print(
            f"Error: Invalid datetime format '{datetime_str}'. Please use YYYY-MM-DDTHH:MM format."
        )
        sys.exit(1)


def parse_attendees(attendees_str: str) -> List[Dict[str, str]]:
    """
    Parse attendees string into a list of attendee dictionaries.

    Args:
        attendees_str: Comma-separated list of email addresses

    Returns:
        List of attendee dictionaries
    """
    if not attendees_str:
        return []

    return [{"email": email.strip()} for email in attendees_str.split(",") if email.strip()]


def main():
    """Main entry point for the calendar tool CLI."""
    parser = argparse.ArgumentParser(description="Google Calendar Tool CLI")
    parser.add_argument("--credentials", help="Path to the credentials JSON file", required=True)
    parser.add_argument(
        "--token", help="Path to store/read the token file", default="calendar_token.json"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # upcoming events command
    upcoming_parser = subparsers.add_parser("upcoming", help="Get upcoming events")
    upcoming_parser.add_argument(
        "--max", type=int, default=10, help="Maximum number of events to return"
    )
    upcoming_parser.add_argument(
        "--calendar", default="primary", help="Calendar ID to fetch events from"
    )
    upcoming_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # list calendars command
    calendars_parser = subparsers.add_parser("calendars", help="List available calendars")
    calendars_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # get event details command
    event_parser = subparsers.add_parser("event", help="Get event details")
    event_parser.add_argument("event_id", help="ID of the event to fetch")
    event_parser.add_argument(
        "--calendar", default="primary", help="Calendar ID the event belongs to"
    )
    event_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # date range command
    range_parser = subparsers.add_parser("range", help="Get events in a date range")
    range_parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    range_parser.add_argument("end_date", help="End date (YYYY-MM-DD)")
    range_parser.add_argument(
        "--calendar", default="primary", help="Calendar ID to fetch events from"
    )
    range_parser.add_argument(
        "--max", type=int, default=100, help="Maximum number of events to return"
    )
    range_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # create event command
    create_parser = subparsers.add_parser("create", help="Create a new event")
    create_parser.add_argument("summary", help="Title of the event")
    create_parser.add_argument("start_time", help="Start time (YYYY-MM-DDTHH:MM)")
    create_parser.add_argument("end_time", help="End time (YYYY-MM-DDTHH:MM)")
    create_parser.add_argument("--description", default="", help="Description of the event")
    create_parser.add_argument("--location", default="", help="Location of the event")
    create_parser.add_argument(
        "--attendees", default="", help="Comma-separated list of attendee email addresses"
    )
    create_parser.add_argument("--calendar", default="primary", help="Calendar ID to add event to")
    create_parser.add_argument("--timezone", default="UTC", help="Timezone for the event")
    create_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # update event command
    update_parser = subparsers.add_parser("update", help="Update an existing event")
    update_parser.add_argument("event_id", help="ID of the event to update")
    update_parser.add_argument("--summary", help="New title of the event")
    update_parser.add_argument("--start_time", help="New start time (YYYY-MM-DDTHH:MM)")
    update_parser.add_argument("--end_time", help="New end time (YYYY-MM-DDTHH:MM)")
    update_parser.add_argument("--description", help="New description of the event")
    update_parser.add_argument("--location", help="New location of the event")
    update_parser.add_argument(
        "--attendees", help="New comma-separated list of attendee email addresses"
    )
    update_parser.add_argument(
        "--calendar", default="primary", help="Calendar ID the event belongs to"
    )
    update_parser.add_argument("--timezone", default="UTC", help="Timezone for the event")
    update_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # delete event command
    delete_parser = subparsers.add_parser("delete", help="Delete an event")
    delete_parser.add_argument("event_id", help="ID of the event to delete")
    delete_parser.add_argument(
        "--calendar", default="primary", help="Calendar ID the event belongs to"
    )

    args = parser.parse_args()

    # Create the calendar tool
    cal_tool = GoogleCalendarTool(credentials_path=args.credentials, token_path=args.token)

    try:
        # Handle different commands
        if args.command == "upcoming":
            events = cal_tool.get_upcoming_events(max_results=args.max, calendar_id=args.calendar)
            if hasattr(args, "json") and args.json:
                print(json.dumps(events, indent=2))
            else:
                display_events(events)

        elif args.command == "calendars":
            calendars = cal_tool.get_calendar_list()
            if hasattr(args, "json") and args.json:
                print(json.dumps(calendars, indent=2))
            else:
                display_calendars(calendars)

        elif args.command == "event":
            event = cal_tool.get_event_details(event_id=args.event_id, calendar_id=args.calendar)
            if hasattr(args, "json") and args.json:
                print(json.dumps(event, indent=2))
            else:
                print(f"Event: {event.get('summary', 'No title')}")
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                print(f"When: {start} to {end}")
                print(f"Where: {event.get('location', 'No location specified')}")
                print(f"Description: {event.get('description', 'No description')}")

        elif args.command == "range":
            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)
            events = cal_tool.get_events_by_date_range(
                start_date=start_date,
                end_date=end_date,
                calendar_id=args.calendar,
                max_results=args.max,
            )
            if hasattr(args, "json") and args.json:
                print(json.dumps(events, indent=2))
            else:
                display_events(events)

        elif args.command == "create":
            start_time = parse_datetime(args.start_time)
            end_time = parse_datetime(args.end_time)
            attendees = parse_attendees(args.attendees)

            event = cal_tool.create_event(
                summary=args.summary,
                start_time=start_time,
                end_time=end_time,
                description=args.description,
                location=args.location,
                attendees=attendees,
                calendar_id=args.calendar,
                timezone=args.timezone,
            )

            if hasattr(args, "json") and args.json:
                print(json.dumps(event, indent=2))
            else:
                print("Event created successfully!")
                print(f"Title: {event.get('summary', 'No title')}")
                print(f"ID: {event.get('id', 'Unknown')}")
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                print(f"When: {start} to {end}")
                print(f"Where: {event.get('location', 'No location specified')}")
                print(f"Description: {event.get('description', 'No description')}")

        elif args.command == "update":
            # Parse the parameters
            start_time = parse_datetime(args.start_time) if args.start_time else None
            end_time = parse_datetime(args.end_time) if args.end_time else None
            attendees = parse_attendees(args.attendees) if args.attendees is not None else None

            event = cal_tool.update_event(
                event_id=args.event_id,
                summary=args.summary,
                start_time=start_time,
                end_time=end_time,
                description=args.description,
                location=args.location,
                attendees=attendees,
                calendar_id=args.calendar,
                timezone=args.timezone,
            )

            if hasattr(args, "json") and args.json:
                print(json.dumps(event, indent=2))
            else:
                print("Event updated successfully!")
                print(f"Title: {event.get('summary', 'No title')}")
                print(f"ID: {event.get('id', 'Unknown')}")
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                print(f"When: {start} to {end}")
                print(f"Where: {event.get('location', 'No location specified')}")
                print(f"Description: {event.get('description', 'No description')}")

        elif args.command == "delete":
            success = cal_tool.delete_event(event_id=args.event_id, calendar_id=args.calendar)

            if success:
                print(f"Event with ID {args.event_id} was successfully deleted.")
            else:
                print(f"Failed to delete event with ID {args.event_id}.")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
