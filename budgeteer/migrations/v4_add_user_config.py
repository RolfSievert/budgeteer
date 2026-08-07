from .migration import Migration


def add_user_config_migration() -> Migration:
    return Migration(
        description="Add user config",
        up="""
        CREATE TABLE user_config (
            backup_dir TEXT,
            db_path TEXT
        )
        """,
        down="""
        DROP TABLE user_config
        """,
    )
