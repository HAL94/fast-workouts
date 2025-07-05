import datetime


def format_to_local_time(date: datetime):
    return date.astimezone().strftime("%Y-%m-%d %H:%M:%S")
