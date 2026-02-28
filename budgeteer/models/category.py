from datetime import datetime
from typing import NamedTuple


class Category(NamedTuple):
    id: int
    created_at: datetime
    name: str
    description: str | None
