from pathlib import Path
from typing import NamedTuple


class UserSettings(NamedTuple):
    db_path: Path
    backup_dir: Path | None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(db_path={self.db_path}, backup_dir={self.backup_dir})"

    def is_equal(self, other: UserSettings | None):
        return (
            other is not None
            and self.db_path == other.db_path
            and self.backup_dir == other.backup_dir
        )
