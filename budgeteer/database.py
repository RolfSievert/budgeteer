import csv
import sqlite3
from datetime import date, datetime
from pathlib import Path

from budgeteer.entities.category import Category, category_from_sql
from budgeteer.entities.expense import Expense, expense_from_sql
from budgeteer.entities.metadata import Metadata, metadata_from_sql
from budgeteer.migrations import (
    v1_add_category,
    v2_add_expense,
    v3_add_expense_description,
    v4_add_metadata,
)


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

        db_version = self._get_version()

        # WARNING: migrations must stay in order!
        migrations = [
            v1_add_category.add_category_migration(),
            v2_add_expense.add_expense_migration(),
            v3_add_expense_description.add_description_migration(),
            v4_add_metadata.add_metadata_migration(),
        ]

        if db_version >= len(migrations):
            return  # no new migration
        elif db_version > len(migrations):
            raise RuntimeError(
                "Database is newer than budgeteer, please update budgeteer to the latest version"
            )

        print(f"Applying {len(migrations) - db_version} migrations...")
        for i in range(db_version, len(migrations)):
            migration = migrations[i]
            m_version = i + 1
            migration.up(self.connection)
            self._set_version(m_version)
            print(f" - Applied migration ({m_version}): {migration.description}")

        print()

    def get_categories(self) -> list[Category]:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Category.table_name()}
            """
        )

        return [category_from_sql(e) for e in result.fetchall()]

    def get_category_map(self) -> dict[int, Category]:
        return {c.id: c for c in self.get_categories()}

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

    def get_expenses(
        self, start: date | None = None, before: date | None = None
    ) -> list[Expense]:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        query = f"SELECT * FROM {Expense.table_name()}"
        conditions = []
        params = []

        if start is not None:
            conditions.append(
                "(year > ? OR (year = ? AND month > ?) OR (year = ? AND month = ? AND day >= ?))"
            )
            params.extend(
                [
                    start.year,
                    start.year,
                    start.month,
                    start.year,
                    start.month,
                    start.day,
                ]
            )

        if before is not None:
            conditions.append(
                "(year < ? OR (year = ? AND month < ?) OR (year = ? AND month = ? AND day < ?))"
            )
            params.extend(
                [
                    before.year,
                    before.year,
                    before.month,
                    before.year,
                    before.month,
                    before.day,
                ]
            )

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = cursor.execute(query, params)

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

    def update_expense(self, expense: Expense) -> Expense:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            UPDATE {Expense.table_name()}
            SET
                name = ?,
                price = ?,
                year = ?,
                month = ?,
                day = ?,
                description = ?,
                category_id = ?
            WHERE id = ?
            """,
            (
                expense.name,
                expense.price,
                expense.year,
                expense.month,
                expense.day,
                expense.description,
                expense.category_id,
                expense.id,
            ),
        )

        self.connection.commit()

        return expense

    def delete_expense(self, expense_id: int) -> None:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            DELETE FROM {Expense.table_name()}
            WHERE id = ?
            """,
            (expense_id,),
        )

        self.connection.commit()

    def export_expenses_to_csv(self, csv_path: Path) -> bool:
        expenses = self.get_expenses()
        if not expenses:
            return True  # nothing to export

        category_map = {c.id: c.name for c in self.get_categories()}

        expenses_dicts = [e.to_sql() for e in expenses]

        for d in expenses_dicts:
            category_id = d["category_id"]
            if category_id is not None:
                d["category"] = category_map[category_id]
            d.pop("category_id")

        with open(csv_path, "x", newline="") as f:
            writer = csv.DictWriter(
                f, delimiter=";", fieldnames=expenses_dicts[0].keys()
            )

            writer.writeheader()
            writer.writerows(expenses_dicts)

        return True

    def get_metadata(self) -> Metadata:
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()

        result = cursor.execute(
            f"""
            SELECT * from {Metadata.table_name()}
            LIMIT 1
            """
        )

        db_metadata = result.fetchone()

        if db_metadata is not None:
            return metadata_from_sql(db_metadata)

        cursor.close()
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        metadata = Metadata(None)
        cursor.execute(
            f"""
            INSERT INTO {Metadata.table_name()} VALUES({metadata.sql_values()})
            """,
            metadata.to_sql(),
        )
        self.connection.commit()

        return metadata

    def update_metadata(self, metadata: Metadata) -> Metadata:
        self.connection.row_factory = None
        cursor = self.connection.cursor()

        cursor.execute(
            f"""
            UPDATE {Metadata.table_name()}
            SET
                start_page_note = ?
            """,
            (metadata.start_page_note,),
        )

        self.connection.commit()

        return metadata

    def export_metadata_to_csv(self, csv_path: Path) -> bool:
        metadata = self.get_metadata().to_sql()

        with open(csv_path, "x", newline="") as f:
            writer = csv.DictWriter(f, delimiter=";", fieldnames=metadata.keys())

            writer.writeheader()
            writer.writerows([metadata])

        return True
