from datetime import datetime


def localnow() -> datetime:
    return datetime.now().astimezone()


def utcnow() -> datetime:
    from datetime import UTC

    return datetime.now(tz=UTC)
