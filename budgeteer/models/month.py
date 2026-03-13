import datetime
from datetime import date
from typing import NamedTuple


class Month(NamedTuple):
    year: int
    month: int

    def __as_date(self) -> date:
        return date(self.year, self.month, 1)

    def format(self, format) -> str:
        return self.__as_date().strftime(format)

    def __lt__(self, other):
        return (
            self.year < other.year
            or self.year == other.year
            and self.month < other.month
        )

    def __le__(self, other):
        return (
            self.year < other.year
            or self.year == other.year
            and self.month <= other.month
        )

    def __gt__(self, other):
        return (
            self.year > other.year
            or self.year == other.year
            and self.month > other.month
        )

    def __ge__(self, other):
        return (
            self.year > other.year
            or self.year == other.year
            and self.month >= other.month
        )

    def __eq__(self, other):
        return self.year == other.year and self.month == other.month

    def __ne__(self, other) -> bool:
        return self.year != other.year or self.month != other.month


def parse_month(text: str, format: str) -> Month:
    date: datetime.date = datetime.date.strptime(text, format)  # ty:ignore[unresolved-attribute]
    return Month(year=date.year, month=date.month)
