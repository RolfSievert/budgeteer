from .migration import Migration


def add_category_migration() -> Migration:
    return Migration(
        description="Create the categories table",
        up="""
        CREATE TABLE categories(
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT
        )
        """,
        down="""
        DROP TABLE categories
        """,
    )
