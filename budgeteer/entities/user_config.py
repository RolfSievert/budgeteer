from typing import NamedTuple


class UserConfig(NamedTuple):
    backup_dir: str | None
    start_page_note: str | None
    db_path: str | None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(backup_dir={self.backup_dir}, start_page_note={self.start_page_note}, db_path={self.db_path})"

    def to_sql(self) -> dict:
        return {
            "backup_dir": self.backup_dir,
            "start_page_note": self.start_page_note,
            "db_path": self.db_path,
        }

    def sql_values(self) -> str:
        """
        Returns placeholder names for the object, like ":id, :created_at, ..."
        """
        prepended = [":" + tag for tag in self.to_sql()]
        return ", ".join(prepended)

    def table_name() -> str:
        return "user_config"


def user_config_from_sql(sql: dict) -> UserConfig:
    return UserConfig(
        backup_dir=sql["backup_dir"],
        start_page_note=sql["start_page_note"],
        db_path=sql["db_path"],
    )
