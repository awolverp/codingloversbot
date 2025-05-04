from datetime import timedelta, datetime, timezone
import typing

from . import env


def is_admin(id: int) -> bool:
    """
    Returns `True` if id is admin of bot
    """
    return id in env.ADMINS


def format_datetime(
    dt: typing.Union[int, float, datetime, None] = None, fmt: str = "%Y.%m.%d - %H:%M UTC"
) -> str:
    """
    Convert datetime (or timestamp) to string (timezone is UTC)
    """
    if dt is None:
        dt = datetime.now()

    if isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt, tz=timezone.utc).strftime(fmt)

    return dt.astimezone(timezone.utc).strftime(fmt)


def format_duration(dt: typing.Union[int, float, timedelta]):
    """
    Convert timedelta (or timestamp) to string
    """
    if isinstance(dt, timedelta):
        dt = dt.total_seconds()

    if dt > 24 * 60 * 60:
        return "{}d {:02d}:{:02d}".format(
            int(dt / (24 * 60 * 60)), int((dt / (60 * 60)) % 24), int((dt / 60) % 60)
        )

    return "{:02d}:{:02d}".format(int(dt / (60 * 60)), int((dt / 60) % 60))
