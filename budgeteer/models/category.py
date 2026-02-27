from typing import NamedTuple
from datetime import datetime


class Category(NamedTuple):
    id: int
    created_at: datetime
    name: str
    description: str | None
