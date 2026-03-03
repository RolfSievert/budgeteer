from .migration import Migration


def add_expense_migration() -> Migration:
    return Migration(
        version=2,
        description="Create the expenses table",
        up="""
        CREATE TABLE expenses(
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            year INT NOT NULL,
            month INT NOT NULL,
            day INT NOT NULL,
            category_id INT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
                ON DELETE SET NULL      -- set the value to null if category gets deleted
        )
        """,
        down="""
        DROP TABLE expenses
        """,
    )
