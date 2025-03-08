## Google Calendar Tool

The `sanity_check.py` script provides a simple way to test connectivity to the Google Calendar API and list your upcoming calendar events.

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

4. **Run the Sanity Check Script**

   The script accepts command line arguments for credentials and token paths:

   ```bash
   # Basic usage (uses default paths)
   python naomi_core/tools/calendar/sanity_check.py
   
   # Specifying custom paths for credentials and token
   python naomi_core/tools/calendar/sanity_check.py \
     --credentials=/path/to/secrets/client_secret.json \
     --token=/path/to/store/token.json
   ```

   The first time you run the script, it will open a browser window asking you to authorize the application to access your Google Calendar. After authorization, a token file will be created to store your access tokens.

### Command Line Arguments

The `sanity_check.py` script accepts the following command line arguments:

- `--credentials`: Path to the credentials JSON file (default: "secrets/client_secret_671906164382-20aemumt8akm5hjqfmev9hl7frl8i47m.apps.googleusercontent.com.json")
- `--token`: Path to store/read the token file (default: "token.json")

### What the Script Does

The script:
1. Authenticates with Google Calendar API using OAuth 2.0
2. Fetches the next 10 upcoming events from your primary calendar
3. Displays the start time and summary of each event

This is useful for:
- Verifying your Google Calendar API credentials are working
- Testing that authentication is set up correctly
- Checking what events are coming up in your calendar

### Notes

- The script shows your 10 upcoming events (not just today's events)
- It uses your primary Google Calendar by default
- If you need to reauthorize, delete the token file
- Make sure both credentials and token files are kept secure and not shared publicly
- The script uses a desktop OAuth flow that launches a browser for authentication
