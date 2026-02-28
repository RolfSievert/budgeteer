from budgeteer.models.expense import Expense
from budgeteer.models.category import Category
from budgeteer.migrations import v1_add_category, v2_add_expense

from pathlib import Path
import sqlite3
from datetime import date, datetime


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.connection = sqlite3.connect(path)
        # Holds the version of the database migrations
        self._schema_table = "schema_version"

        # migrate the database if needed
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

    def _is_initialized(self) -> bool:
        cursor = self.connection.cursor()

        # check if the table exists, returns empty list otherwise
        table_match = cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self._schema_table}'"
        )
        return len(table_match.fetchall()) > 0

    def _initialize(self):
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._schema_table} (
                version INTEGER PRIMARY KEY
            );
            """
        )

        version = (0,)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO schema_version VALUES(?)
            """,
            version,
        )
        self.connection.commit()

    def _set_version(self, version: int) -> None:
        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE schema_version
            SET version = ?
            where version != -1
            """,
            (version,),
        )
        self.connection.commit()

    def _get_version(self) -> int:
        cursor = self.connection.cursor()
        res = cursor.execute(
            f"""
            select version from {self._schema_table}
            """
        )
        return res.fetchone()[0]

    def _migrate(self):
        if not self._is_initialized():
            print("Initializing database (only happens with a new database)")
            self._initialize()

        version = self._get_version()

        # NOTE: these must be in order!
        migrations = [
            v1_add_category.add_category_migration(),
            v2_add_expense.add_expense_migration(),
        ]

        for migration in sorted(migrations, key=lambda x: x.version):
            if migration.version > version:
                print(f"Applied migration: {migration.description}")
                migration.up(self.connection)
                self._set_version(migration.version)
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
