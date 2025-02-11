import pytz
import tzlocal

from datetime import datetime
from typing import Any
from googleapiclient.discovery import build

TZ = pytz.timezone(tzlocal.get_localzone().key)


class CalendarEvent:
    def __init__(self, summary: str, start: datetime, end: datetime):
        self.summary = summary
        self.start = start
        self.end = end
        self.minute_duration = (end - start).seconds // 60

    def to_simple_time(self, t: datetime):
        return t.strftime("%H:%M")

    def __repr__(self):
        return (
            f"{self.summary} - "
            f"{self.to_simple_time(self.start)} - "
            f"{self.to_simple_time(self.end)} "
            f"({self.minute_duration / 60:.1f} hour(s))"
        )


def calendar_service(creds):
    return build("calendar", "v3", credentials=creds)


def get_events(service: Any, date: Any):
    start_of_day = TZ.localize(datetime.combine(date, datetime.min.time())).isoformat()
    end_of_day = TZ.localize(datetime.combine(date, datetime.max.time())).isoformat()

    all_events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []

    for e in all_events["items"]:
        start = datetime.fromisoformat(e["start"]["dateTime"])
        end = datetime.fromisoformat(e["end"]["dateTime"])
        events.append(CalendarEvent(e["summary"], start, end))

    return events
