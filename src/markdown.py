from datetime import datetime
from typing import List


class MarkdownWriter:
    def __init__(self, f):
        self.f = f

    def text(self, text):
        self.f.write(f"{text}\n")

    def h1(self, text):
        self.f.write(f"# {text}\n")

    def h2(self, text):
        self.f.write(f"## {text}\n")

    def h3(self, text):
        self.f.write(f"### {text}\n")

    def h4(self, text):
        self.f.write(f"#### {text}\n")

    def front_matter(self, type: str, date: datetime):
        self.f.write(f"---\n")
        self.f.write(f"type: {type}\n")
        self.f.write(f"date: {date.strftime("%Y-%m-%d")}\n")
        self.f.write(f"---\n")

    def table(self, headers: List[str], rows: List[List[str]]):
        self.f.write("|" + "|".join(headers) + "|\n")
        self.f.write("|" + "|".join(["---"] * len(headers)) + "|\n")

        for row in rows:
            self.f.write("|" + "|".join(row) + "|\n")

    def close(self):
        self.f.close()
