from datetime import datetime


def localnow() -> datetime:
    return datetime.now().astimezone()
