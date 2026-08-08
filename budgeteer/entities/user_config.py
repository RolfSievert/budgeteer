from pathlib import Path
from typing import NamedTuple


class UserConfig(NamedTuple):
    backup_dir: Path | None
    db_path: Path | None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(backup_dir={self.backup_dir}, db_path={self.db_path})"
