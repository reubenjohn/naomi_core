## Google Calendar Tool

This package provides tools for working with the Google Calendar API. It includes:

1. `g_cal_tool.py` - A reusable API client class
2. `cal_tool_runner.py` - A CLI tool for interacting with Google Calendar
3. `sanity_check.py` - A simple script for testing API connectivity

### Setup Instructions

1. **Install Required Dependencies**

   The project uses Poetry for dependency management. All required packages are already included in the project's `pyproject.toml`.

   ```bash
   # From the project root
   cd /path/to/naomi_core
   poetry install
   ```

2. **Create a Google Cloud Project**

   1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
   2. Create a new project or select an existing one
   3. Enable the Google Calendar API:
      - In the navigation menu, select "APIs & Services" > "Library"
      - Search for "Google Calendar API" and enable it

3. **Create OAuth 2.0 Credentials**

   1. In the Google Cloud Console, navigate to "APIs & Services" > "Credentials"
   2. Click "Create Credentials" and select "OAuth client ID"
   3. Select "Desktop application" as the application type (the script uses InstalledAppFlow for local authentication)
   4. Name your OAuth client and click "Create"
   5. Download the credentials JSON file by clicking the download icon
   6. Place it in a secure directory (like a `secrets` folder)

### Using the Calendar Tool CLI

The `cal_tool_runner.py` script provides a comprehensive CLI for working with Google Calendar:

```bash
# Get upcoming events (default: next 10 events)
python -m naomi_core.tools.calendar.cal_tool_runner \
  --credentials=/path/to/secrets/client_secret.json \
  --token=/path/to/token.json \
  upcoming [--max 5] [--calendar primary] [--json]

# List available calendars
python -m naomi_core.tools.calendar.cal_tool_runner \
  --credentials=/path/to/secrets/client_secret.json \
  --token=/path/to/token.json \
  calendars [--json]

# Get details for a specific event
python -m naomi_core.tools.calendar.cal_tool_runner \
  --credentials=/path/to/secrets/client_secret.json \
  --token=/path/to/token.json \
  event EVENT_ID [--calendar primary] [--json]

# Get events in a specific date range
python -m naomi_core.tools.calendar.cal_tool_runner \
  --credentials=/path/to/secrets/client_secret.json \
  --token=/path/to/token.json \
  range 2025-01-01 2025-12-31 [--calendar primary] [--max 100] [--json]
```

### Command Line Arguments

Common arguments for all commands:
- `--credentials`: Path to the credentials JSON file (required)
- `--token`: Path to store/read the token file (default: "token.json")

Command-specific arguments:
- `upcoming`: Get upcoming events
  - `--max`: Maximum number of events to return (default: 10)
  - `--calendar`: Calendar ID to fetch events from (default: "primary")
  - `--json`: Output in JSON format
  
- `calendars`: List all available calendars
  - `--json`: Output in JSON format
  
- `event`: Get details for a specific event
  - `event_id`: ID of the event to fetch (required)
  - `--calendar`: Calendar ID the event belongs to (default: "primary")
  - `--json`: Output in JSON format
  
- `range`: Get events in a specific date range
  - `start_date`: Start date in YYYY-MM-DD format (required)
  - `end_date`: End date in YYYY-MM-DD format (required)
  - `--calendar`: Calendar ID to fetch events from (default: "primary")
  - `--max`: Maximum number of events to return (default: 100)
  - `--json`: Output in JSON format

### Using the GoogleCalendarTool Class

For programmatic access, import and use the `GoogleCalendarTool` class:

```python
from naomi_core.tools.calendar.g_cal_tool import GoogleCalendarTool

# Initialize the calendar tool
cal_tool = GoogleCalendarTool(
    credentials_path="/path/to/client_secret.json",
    token_path="/path/to/token.json"
)

# Get upcoming events
events = cal_tool.get_upcoming_events(max_results=5)
for event in events:
    print(f"{cal_tool.format_event_time(event)} - {event.get('summary', 'No title')}")

# Get list of available calendars
calendars = cal_tool.get_calendar_list()

# Get events for a specific date range
import datetime
start = datetime.datetime(2025, 1, 1)
end = datetime.datetime(2025, 12, 31)
events = cal_tool.get_events_by_date_range(start, end)
```

### Sanity Check Script

The `sanity_check.py` script provides a simple way to test connectivity:

```bash
# Basic usage
python -m naomi_core.tools.calendar.sanity_check \
  --credentials=/path/to/secrets/client_secret.json \
  --token=/path/to/token.json
```

### Notes

- The first time you run any of these tools, a browser window will open asking you to authorize the application
- After authorization, a token file will be created to store your access tokens
- The default calendar is your primary Google Calendar
- If you need to reauthorize, delete the token file
- Make sure both credentials and token files are kept secure and not shared publicly
- These tools use a desktop OAuth flow that launches a browser for authentication
