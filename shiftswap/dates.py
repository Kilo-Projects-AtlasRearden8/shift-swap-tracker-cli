"""Date handling and validation helpers."""

from __future__ import annotations

import datetime as dt
from typing import Optional


def parse_date(value: str) -> dt.date:
    """Parse a YYYY-MM-DD date string into a :class:`datetime.date`.

    Raises ``ValueError`` if the string is not a valid calendar date.
    """
    if not isinstance(value, str):
        raise ValueError(f"Date must be a string, got {type(value).__name__}")
    try:
        return dt.date.fromisoformat(value.strip())
    except ValueError as exc:  # pragma: no cover - re-raised with clearer message
        raise ValueError(f"Invalid date {value!r}: expected YYYY-MM-DD") from exc


def normalize_date(value: str) -> str:
    """Return the canonical YYYY-MM-DD form of a date string."""
    return parse_date(value).isoformat()


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in the given month."""
    return _days_in_month(year, month)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = dt.date(year + 1, 1, 1)
    else:
        next_month = dt.date(year, month + 1, 1)
    return (next_month - dt.date(year, month, 1)).days


def is_valid_date(value: str) -> bool:
    """Return True if ``value`` is a valid YYYY-MM-DD date string."""
    try:
        parse_date(value)
    except ValueError:
        return False
    return True


def date_range(start: str, end: str):
    """Yield every date (inclusive) between two YYYY-MM-DD strings."""
    d0 = parse_date(start)
    d1 = parse_date(end)
    if d0 > d1:
        raise ValueError(f"start date {start!r} is after end date {end!r}")
    current = d0
    while current <= d1:
        yield current.isoformat()
        current += dt.timedelta(days=1)


def week_bounds(date_value: str):
    """Return (monday, sunday) ISO date strings for the week containing ``date_value``."""
    d = parse_date(date_value)
    monday = d - dt.timedelta(days=d.weekday())
    sunday = monday + dt.timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


def period_dates(period: str, ref: Optional[str] = None) -> list:
    """Return the list of ISO date strings for a named period.

    Supported periods: ``day``, ``week``, ``month``.
    """
    today = parse_date(ref) if ref else dt.date.today()
    if period == "day":
        return [today.isoformat()]
    if period == "week":
        monday = today - dt.timedelta(days=today.weekday())
        return [(monday + dt.timedelta(days=i)).isoformat() for i in range(7)]
    if period == "month":
        year, month = today.year, today.month
        return [
            dt.date(year, month, day).isoformat()
            for day in range(1, _days_in_month(year, month) + 1)
        ]
    raise ValueError(f"Unknown period {period!r}: expected day, week, or month")


def add_days(date_value: str, days: int) -> str:
    """Return the ISO date string ``days`` days after (or before) ``date_value``."""
    d = parse_date(date_value) + dt.timedelta(days=days)
    return d.isoformat()


def diff_days(a: str, b: str) -> int:
    """Return the number of days between two ISO date strings (b - a)."""
    return (parse_date(b) - parse_date(a)).days