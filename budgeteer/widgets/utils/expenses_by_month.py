from datetime import date
from typing import NamedTuple

from budgeteer.models.expense import Expense


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


def expenses_by_month(expenses: list[Expense]) -> dict[Month, list[Expense]]:
    res: dict[Month, list[Expense]] = {}

    for e in expenses:
        month = Month(year=e.year, month=e.month)
        if month not in res:
            res[month] = []
        res[month].append(e)

    return res
