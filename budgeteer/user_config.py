import json
from pathlib import Path

from platformdirs import PlatformDirs

from budgeteer.entities.user_config import UserConfig


def data_dir() -> Path:
    dirs = PlatformDirs("budgeteer", "RolfSievert")
    return dirs.user_data_path


def user_config_path() -> Path:
    return data_dir() / "user_config.json"


def get_user_config() -> UserConfig:
    p = user_config_path()
    if not p.is_file():
        return UserConfig(None, None)

    with open(p, "r") as f:
        data = json.load(f)

    user_config = UserConfig(**data)

    return user_config


def set_user_config(config: UserConfig) -> UserConfig:
    p = user_config_path()
    with open(p, "w") as f:
        json.dump(config._asdict(), f)

    return config
