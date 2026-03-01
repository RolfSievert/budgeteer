from datetime import date, datetime
from typing import NamedTuple

from budgeteer.str_utils import str_to_time


class Expense(NamedTuple):
    name: str
    year: int
    month: int
    day: int
    category_id: int | None
    created_at: datetime
    id: int = -1  # id is -1 if not added to the database

    def date(self) -> date:
        return date(self.year, self.month, self.day)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, name={self.name}, category_id={self.category_id})"

    def to_sql(self) -> dict:
        return {
            "id": self.id if self.id != -1 else None,
            "created_at": self.created_at,
            "name": self.name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "category_id": self.category_id,
        }

    def sql_values(self) -> str:
        """
        Returns placeholder names for the object, like ":id, :created_at, ..."
        """
        prepended = [":" + tag for tag in self.to_sql().keys()]
        return ", ".join(prepended)

    def table_name() -> str:
        return "expenses"


def expense_from_sql(sql: dict) -> Expense:
    created_at = str_to_time(sql["created_at"])
    if not created_at:
        raise RuntimeError(f"Could not parse created_at: {created_at}")

    return Expense(
        id=sql["id"],
        created_at=created_at,
        name=sql["name"],
        year=sql["year"],
        month=sql["month"],
        day=sql["day"],
        category_id=sql["category_id"],
    )
