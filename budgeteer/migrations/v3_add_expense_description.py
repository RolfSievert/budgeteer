from .migration import Migration


def add_description_migration() -> Migration:
    return Migration(
        description="Add description to expenses",
        up="""
        ALTER TABLE expenses
        ADD COLUMN description TEXT
        """,
        down="""
        ALTER TABLE expenses DROP COLUMN description
        """,
    )
