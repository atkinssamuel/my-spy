import os
import pytz

from datetime import datetime, timedelta
from google_auth_wrapper import credentials
from dotenv import load_dotenv
from src.calendar import get_events, calendar_service


if __name__ == "__main__":
    load_dotenv()
    creds = credentials(
        scopes=[os.getenv("GOOGLE_SCOPE")],
        client=os.getenv("GOOGLE_CLIENT_ID"),
        secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        path_to_refresh="refresh.txt",
    )

    service = calendar_service(creds)

    date = datetime.now().date()

    events = get_events(service, date)

    for e in events:
        print(e)
