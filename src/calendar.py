import pytz
import tzlocal
import re

from datetime import datetime, timedelta
from typing import Any, List
from googleapiclient.discovery import build

TZ = pytz.timezone(tzlocal.get_localzone().key)


class CalendarEvent:
    def __init__(self, summary: str, start: datetime, end: datetime, tags: List[str]):
        self.summary = summary
        self.start = start
        self.end = end
        self.tags = tags

        self.minute_duration = (end - start).seconds // 60

    def to_simple_time(self, t: datetime):
        return t.strftime("%H:%M")

    def __repr__(self):
        return (
            f"{self.summary} - "
            f"{self.to_simple_time(self.start)} - "
            f"{self.to_simple_time(self.end)} "
            f"({self.minute_duration / 60:.2f} hour(s))"
        )


def calendar_service(creds):
    return build("calendar", "v3", credentials=creds)


def get_events(service: Any, start_date: Any, end_date: Any):
    start_of_day = TZ.localize(
        datetime.combine(start_date, datetime.min.time())
    ).isoformat()
    end_of_day = TZ.localize(
        datetime.combine(end_date, datetime.max.time())
    ).isoformat()

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

    tagged_events = []

    work_event_summaries = set(["US Bank", "Entrepreneurship Block", "Learning Block"])
    workout_event_summaries = set(["Gym"])

    for event in all_events["items"]:
        tags = []

        if "description" in event:
            description = event["description"]
            tags = re.findall(r"(#[a-z]*)", description)

        summary = event["summary"].replace("&", "and")

        if summary in work_event_summaries:
            tags.append("#work")

        if summary in workout_event_summaries:
            tags.append("#gym")

        if len(tags) == 0:
            continue

        start = datetime.fromisoformat(event["start"]["dateTime"])
        end = datetime.fromisoformat(event["end"]["dateTime"])

        tagged_events.append(CalendarEvent(summary, start, end, tags))

    return tagged_events


def events_this_week(service: Any):
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())

    return get_events(service, start_of_week, today)
