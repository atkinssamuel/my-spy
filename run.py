import os

from datetime import datetime, timedelta
from google_auth_wrapper import credentials
from dotenv import load_dotenv
from src.calendar import events_this_week, calendar_service
from src.report import WeeklyReport

if __name__ == "__main__":
    load_dotenv()
    creds = credentials(
        scopes=[os.getenv("GOOGLE_SCOPE")],
        client=os.getenv("GOOGLE_CLIENT_ID"),
        secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        path_to_refresh="refresh.txt",
    )

    service = calendar_service(creds)

    # this week

    week_end = datetime.now().date()
    week_start = week_end - timedelta(days=(week_end.isoweekday() % 7))

    print(f"Generating report for {week_start} to {week_end}")

    report = WeeklyReport(service, week_start, week_end)
    report.generate_report()

    # last week

    week_start = week_start - timedelta(days=7)
    week_end = week_start + timedelta(days=6)

    print(f"Generating report for {week_start} to {week_end}")

    report = WeeklyReport(service, week_start, week_end)
    report.generate_report()
