from .migration import Migration


def add_metadata_migration() -> Migration:
    return Migration(
        description="Add vault metadata",
        up="""
        CREATE TABLE metadata (
            start_page_note TEXT
        )
        """,
        down="""
        DROP TABLE metadata
        """,
    )
