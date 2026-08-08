from pathlib import Path
from typing import NamedTuple

from budgeteer.entities.user_settings import UserSettings


class ProgramSettings(NamedTuple):
    user_settings_path: Path
    user_settings: UserSettings
