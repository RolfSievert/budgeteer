from datetime import date, datetime

__date_format = "%Y-%m-%d"


def str_to_date(time: str) -> date | None:
    formats = [__date_format, date.isoformat]

    for format in formats:
        try:
            return date.strptime(time, format)  # ty:ignore[unresolved-attribute]
        except ValueError:
            pass

    return None


def date_to_str(time: date) -> str:
    return time.strftime(__date_format)


def str_to_time(time: str) -> datetime:
    return datetime.fromisoformat(time)


def time_to_str(time: datetime) -> str:
    return time.isoformat()
