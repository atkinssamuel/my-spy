import os
import pandas as pd

from dotenv import load_dotenv
from typing import Any
from src.markdown import MarkdownWriter
from .calendar import get_events
from datetime import timedelta, datetime


def rounded_str(x: Any) -> str:
    return x if isinstance(x, str) else f"{x:.2f}"


class WeeklyReport:
    def __init__(self, service: Any, week_start: Any, week_end: Any):
        load_dotenv()

        self.reports_dir = os.getenv("REPORTS_DIR")

        if self.reports_dir is None:
            raise ValueError("REPORTS_DIR must be set in .env")

        self.service = service
        self.week_start = week_start
        self.week_end = week_end

        self.events = get_events(service, week_start, week_end)

        sunday_0_weekday = week_end.isoweekday() % 7

        self.days_this_week = [
            (week_start + timedelta(days=i)) for i in range(sunday_0_weekday + 1)
        ]

        self.markdown_writer = MarkdownWriter(
            open(
                f"{self.reports_dir}/{week_start.strftime("%Y-%m-%d Weekly Report")}.md",
                "w",
            )
        )

        self.work_dataframe = self.extract_work_dataframe()
        self.fitness_dict = self.extract_fitness_dict()

    def extract_work_dataframe(self) -> pd.DataFrame:
        df_dict = {
            "Event": [],
            **{day.strftime("%A"): [] for day in self.days_this_week},
        }

        tagged_events = [event for event in self.events if "#work" in event.tags]
        unique_event_labels = set([event.summary for event in tagged_events])

        for event_label in unique_event_labels:
            df_dict["Event"].append(event_label)

            for day in self.days_this_week:
                day_events = [
                    event for event in self.events if event.start.date() == day
                ]
                category_hours = (
                    sum(
                        [
                            event.minute_duration
                            for event in day_events
                            if event.summary == event_label
                        ]
                    )
                    / 60
                )

                df_dict[day.strftime("%A")].append(category_hours)

        return pd.DataFrame.from_dict(df_dict)

    def extract_fitness_dict(self) -> dict:
        fitness_events = [
            event
            for event in self.events
            if set(event.tags) & {"#gym", "#squat", "#bench"}
        ]

        fitness_dict = {"Squat": 0, "Bench": 0, "Gym": 0}

        for event in fitness_events:
            fitness_dict["Gym"] += 1

            if "#squat" in event.tags:
                fitness_dict["Squat"] += 1

            if "#bench" in event.tags:
                fitness_dict["Bench"] += 1

        return fitness_dict

    def generate_daily_dataframe(self, dataframe: pd.DataFrame, label: str):
        self.markdown_writer.text("")
        self.markdown_writer.table(
            [" ", *dataframe.columns[1:]],
            dataframe.map(lambda x: rounded_str(x)).values,
        )
        self.markdown_writer.text(f"^{label}")

    def generate_report(self):
        now = datetime.now()

        self.markdown_writer.front_matter("report", self.week_start)

        self.markdown_writer.text("Tags: #progress-report")
        self.markdown_writer.text("")
        self.markdown_writer.text("[[____reports (goals)]]")
        self.markdown_writer.text("")

        self.markdown_writer.text(f'**{now.strftime("%B %d at %I:%M%p")}**')

        self.markdown_writer.h1(
            f"Week of {self.week_start.strftime("%m/%d/%Y")} - {self.week_end.strftime("%m/%d/%Y")}"
        )

        self.markdown_writer.h4("Fitness")

        keys = list(self.fitness_dict.keys())
        values = list(str(self.fitness_dict[key]) for key in keys)

        self.markdown_writer.table([" ", *keys], [["Total", *values]])
        self.markdown_writer.text("^fitness-total")

        self.markdown_writer.text(
            f"""
```chart
type: bar
id: fitness-total
layout: rows
width: 80%
beginAtZero: true
indexAxis: y
xMax: 6
```"""
        )

        self.markdown_writer.h4("Work")

        # work total table and chart

        unique_work_labels = set(self.work_dataframe["Event"].values)
        total_hours_worked = []

        for label in unique_work_labels:
            total_hours_worked.append(
                self.work_dataframe[self.work_dataframe["Event"] == label]
                .values[0, 1:]
                .sum()
            )
        self.markdown_writer.table(
            [" ", "Hours Worked", "Hours Target"],
            [
                [
                    "Total",
                    rounded_str(rounded_str(sum(total_hours_worked))),
                    rounded_str(6 * 5 + 4),
                ]
            ],
        )
        self.markdown_writer.text("^work-total")
        self.markdown_writer.text(
            f"""
```chart
type: bar
id: work-total
layout: rows
width: 90%
beginAtZero: true
indexAxis: y
xMax: 50
legend: false
labelColors: true
```
"""
        )

        self.markdown_writer.table(
            [" ", *unique_work_labels],
            [["Total", *[rounded_str(h) for h in total_hours_worked]]],
        )

        self.markdown_writer.text("^work-categories")
        self.markdown_writer.text(
            f"""
```chart
type: bar
id: work-categories
layout: rows
width: 90%
beginAtZero: true
indexAxis: y
xMax: 50
legend: false
labelColors: true
```
"""
        )

        # work daily table and chart

        self.generate_daily_dataframe(self.work_dataframe, "work-daily")
        self.markdown_writer.text(
            f"""
```chart
type: bar
id: work-daily
layout: rows
width: 80%
beginAtZero: true
yMax: 12
```"""
        )

        # individual day summaries

        # self.days_this_week: List[Any] (.date() objects)
        for day in self.days_this_week:
            self.markdown_writer.h2(day.strftime("%A - %m/%d/%Y"))

            hours_worked = (
                self.work_dataframe.loc[:, day.strftime("%A")].astype(float).sum()
            )

            self.markdown_writer.text("")

            target_hours = 6

            if day.weekday() == 6:
                target_hours = 0
            elif day.weekday() == 5:
                target_hours = 4

            self.markdown_writer.text(f"**Target hours**: {target_hours}")
            self.markdown_writer.text(
                f"**Hours worked**: <span style=\"color: {'red' if hours_worked < target_hours else 'green'};\">{rounded_str(hours_worked)}</span>"
            )

            self.markdown_writer.text("")

            day_events = [event for event in self.events if event.start.date() == day]

            self.markdown_writer.table(
                ["Event", "Time", "Hours"],
                [
                    [
                        event.summary,
                        f"{event.start.strftime("%H:%M")} - {event.end.strftime("%H:%M")}",
                        f"{rounded_str(event.minute_duration / 60)}",
                    ]
                    for event in day_events
                ],
            )
            self.markdown_writer.text("")

            headers = [" ", "Hours"]
            rows = [
                [
                    l,
                    rounded_str(
                        self.work_dataframe.loc[
                            self.work_dataframe["Event"] == l,
                            day.strftime("%A"),
                        ].values[0]
                    ),
                ]
                for l in unique_work_labels
            ]

            self.markdown_writer.table(headers, rows)
            self.markdown_writer.text(f"^{day.strftime("%A")}")
            self.markdown_writer.text(
                f"""
```chart
type: bar
id: {day.strftime("%A")}
layout: rows
width: 80%
beginAtZero: true
indexAxis: y
xMax: 10
```
"""
            )

        self.markdown_writer.close()
