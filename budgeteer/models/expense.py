from datetime import date, datetime
from typing import NamedTuple


class Expense(NamedTuple):
    name: str
    date: date
    category_id: int | None
    id: int = -1  # id is -1 if not added to the database
    created_at: datetime = datetime.now()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, name={self.name}, category_id={self.category_id})"

    def to_sql(self) -> dict:
        return {
            "id": self.id if self.id != -1 else None,
            "created_at": self.created_at,
            "name": self.name,
            "date": self.date,
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
    return Expense(
        id=sql["id"],
        created_at=sql["created_at"],
        name=sql["name"],
        date=sql["date"],
        category_id=sql["category_id"],
    )
