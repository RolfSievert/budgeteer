from typing import NamedTuple
from datetime import date, datetime


class Expense(NamedTuple):
    id: int
    created_at: datetime
    name: str
    date: date
    category_id: int | None

    def __str__(self) -> str:
        return (
            f"Expense(id={self.id}, name={self.name}, catogory_id={self.category_id})"
        )
