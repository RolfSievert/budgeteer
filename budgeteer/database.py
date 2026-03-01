import sqlite3
from datetime import date, datetime
from pathlib import Path

from budgeteer.migrations import v1_add_category, v2_add_expense
from budgeteer.models.category import Category, category_from_sql
from budgeteer.models.expense import Expense, expense_from_sql


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.connection = sqlite3.connect(path)
        # Holds the version of the database migrations
        self._schema_table = "schema_version"

        # migrate the database if needed
        self._migrate()

    def _str_to_date(self, time: str) -> date:
        return date.fromisoformat(time)

    def _date_to_str(self, time: date) -> str:
        return time.isoformat()

    def _str_to_time(self, time: str) -> datetime:
        return datetime.fromisoformat(time)

    def _time_to_str(self, time: datetime) -> str:
        return time.isoformat()

    def _is_initialized(self) -> bool:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        # check if the table exists, returns empty list otherwise
        table_match = cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self._schema_table}'"
        )
        return len(table_match.fetchall()) > 0

    def _initialize(self):
        self.connection.row_factory = None
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
        self.connection.row_factory = None
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
        self.connection.row_factory = None
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
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Category.table_name()}
            """
        )

        return [category_from_sql(e) for e in result.fetchall()]

    def get_category(self, id: int) -> Category:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Category.table_name()}
            WHERE id = ?
            LIMIT 1
            """,
            (id,),
        )

        return category_from_sql(result.fetchone())

    def new_category(self, category: Category) -> Category:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            INSERT INTO {Category.table_name()} VALUES({category.sql_values()})
            """,
            category.to_sql(),
        )

        self.connection.commit()

        return category._replace(id=self._last_row_id(cursor))

    def get_expenses(self) -> list[Expense]:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Expense.table_name()}
            """
        )

        return [expense_from_sql(e) for e in result.fetchall()]

    def get_expenses_by_unique_names(self) -> list[Expense]:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Expense.table_name()}
            GROUP BY name
            ORDER BY year DESC, month DESC, day DESC;
            """
        )

        return [expense_from_sql(e) for e in result.fetchall()]

    def _last_row_id(self, cursor: sqlite3.Cursor) -> int:
        """
        Gets the primary key of the last inserted row
        """
        id = cursor.lastrowid

        if not isinstance(id, int):
            raise RuntimeError(
                f"Expected integer primary key, got {id!r} ({type(id).__name__})"
            )

        return id

    def new_expense(self, expense: Expense) -> Expense:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            INSERT INTO {Expense.table_name()} VALUES({expense.sql_values()})
            """,
            expense.to_sql(),
        )

        self.connection.commit()

        return expense._replace(id=self._last_row_id(cursor))

    def update_expense_category(self, expense: Expense, category_id: int) -> Expense:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            UPDATE {Expense.table_name()}
            SET category_id = ?
            WHERE id = ?
            """,
            (category_id, expense.id),
        )

        self.connection.commit()

        return expense._replace(category_id=category_id)

    def export(self, csv_path: Path) -> None:
        print("not implemented")
