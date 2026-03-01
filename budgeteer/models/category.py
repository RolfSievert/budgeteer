from datetime import datetime
from typing import NamedTuple

from budgeteer.str_utils import str_to_time


class Category(NamedTuple):
    name: str
    description: str | None
    created_at: datetime
    id: int = -1  # id is -1 if not added to the database

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, name={self.name}, description={self.description})"

    def to_sql(self) -> dict:
        return {
            "id": self.id if self.id != -1 else None,
            "created_at": self.created_at,
            "name": self.name,
            "description": self.description,
        }

    def sql_values(self) -> str:
        """
        Returns placeholder names for the object, like ":id, :created_at, ..."
        """
        prepended = [":" + tag for tag in self.to_sql().keys()]
        return ", ".join(prepended)

    def table_name() -> str:
        return "categories"


def category_from_sql(sql: dict) -> Category:
    created_at = str_to_time(sql["created_at"])
    if not created_at:
        raise RuntimeError(f"Could not parse date: {created_at}")

    return Category(
        id=sql["id"],
        created_at=created_at,
        name=sql["name"],
        description=sql["description"],
    )
