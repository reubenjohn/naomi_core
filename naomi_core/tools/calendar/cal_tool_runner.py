#!/usr/bin/env python
import argparse
import datetime
import json
import sys
from typing import List, Dict, Any

from .g_cal_tool import GoogleCalendarTool


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


def main():
    """Main entry point for the calendar tool CLI."""
    parser = argparse.ArgumentParser(description="Google Calendar Tool CLI")
    parser.add_argument("--credentials", help="Path to the credentials JSON file", required=True)
    parser.add_argument("--token", help="Path to store/read the token file", default="token.json")

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

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
