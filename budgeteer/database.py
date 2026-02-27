from models.expense import Expense
from models.category import Category
from migrations import v1_add_category, v2_add_expense

from pathlib import Path
import sqlite3
from datetime import date, datetime


class Database:
    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
        self._migrate()

    def __sample_categories(self) -> list[Category]:
        """TODO: REMOVE"""
        return [
            self.new_category(name="category_sport", description="sporty stuf"),
            self.new_category(name="category_clothes", description="on the feet?"),
        ]

    def __sample_expenses(self) -> list[Expense]:
        """TODO: REMOVE"""
        return [
            self.new_expense("expense_sport", date.today(), 2),
            self.new_expense("expense_clothes", date.today(), 1),
        ]

    def _str_to_date(self, time: str) -> date:
        return date.fromisoformat(time)

    def _date_to_str(self, time: date) -> str:
        return time.isoformat()

    def _str_to_time(self, time: str) -> datetime:
        return datetime.fromisoformat(time)

    def _time_to_str(self, time: datetime) -> str:
        return time.isoformat()

    def _ensure_has_version(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            );
            """
        )
        self.connection.commit()

    def _get_version(self) -> int:
        cursor = self.connection.cursor()
        res = cursor.execute(
            """
            select version from schema_version
            """
        )
        return res.fetchone()[0]

    def _migrate(self):
        self._ensure_has_version()
        version = self._get_version()

        # NOTE: these must be in order!
        migrations = [
            v1_add_category.add_category_migration(),
            v2_add_expense.add_expense_migration(),
        ]

        for migration in sorted(migrations, key=lambda x: x.version):
            if migration.version > version:
                migration.up(self.connection)
            else:
                break

    def get_categories(self) -> list[Category]:
        return self.__sample_categories()

    def new_category(self, name: str, description: str) -> Category:
        print("not implemented")
        return Category(
            id=-1, name=name, created_at=datetime.now(), description=description
        )

    def get_expenses(self) -> list[Expense]:
        return self.__sample_expenses()

    def new_expense(self, name: str, date: date, category: int | None) -> Expense:
        print("not implemented")
        return Expense(
            id=-1, created_at=datetime.now(), name=name, date=date, category_id=category
        )

    def update_expense_category(self, expense_id: int, category_id: int) -> Expense:
        print("not implemented")
        return Expense(
            id=expense_id,
            created_at=datetime.now(),
            name="unknown",
            date=date.today(),
            category_id=category_id,
        )

    def export(self, csv_path: Path) -> None:
        print("not implemented")
