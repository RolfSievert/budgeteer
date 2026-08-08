import json
from pathlib import Path

from platformdirs import PlatformDirs

from budgeteer.entities.user_settings import UserSettings


def __default_app_dir() -> Path:
    dirs = PlatformDirs("budgeteer", "RolfSievert")
    return dirs.user_data_path


def default_database_path() -> Path:
    return __default_app_dir() / "database.sqlite"


def default_user_settings_path() -> Path:
    return __default_app_dir() / "user_settings.json"


# returns None if user settings is nonexistent
def get_user_settings(user_settings_path: Path) -> UserSettings:
    user_settings_path = user_settings_path.expanduser()
    if not user_settings_path.is_file():
        raise RuntimeError(f"Not a valid user settings path: {user_settings_path}")

    with open(user_settings_path, "r") as f:
        data = json.load(f)

    user_settings = UserSettings(
        db_path=Path(data["db_path"]), backup_dir=Path(data["backup_dir"])
    )

    return user_settings


def set_user_settings(user_settings_path: Path, settings: UserSettings) -> UserSettings:
    class PathEncoder(json.JSONEncoder):
        def default(self, o: object) -> object:
            if isinstance(o, Path):
                return str(o)
            return super().default(o)

    with open(user_settings_path.expanduser(), "w") as f:
        json.dump(settings._asdict(), f, cls=PathEncoder)

    return settings
