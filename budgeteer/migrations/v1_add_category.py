from .migration import Migration


def add_category_migration() -> Migration:
    return Migration(
        version=1,
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
