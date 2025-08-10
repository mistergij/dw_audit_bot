"""Defines various conversion functions for the bot.
Copyright © 2025 Dnd World

This file is part of Kensa.
Kensa is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

Kensa is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with Kensa. If not, see
<https://www.gnu.org/licenses/>.
"""

from datetime import datetime
from zoneinfo import ZoneInfo


def to_int(value: str) -> str | int:
    if not value:
        return value
    return int(value)


def convert_day(value: int) -> str:
    return f"{value:02d}"


def convert_date(raw_string: str) -> datetime:
    """Convert the raw date strings to EST/EDT datetime objects.

    Arguments:
      after_raw -- The date in the string format YYYY-MM-DD.

    Returns:
      A time-aware datetime object representing the date.
    """
    return datetime.strptime(
        raw_string,
        "%Y-%m-%d",
    ).replace(tzinfo=ZoneInfo("America/New_York"))


def convert_epoch(epoch: float) -> datetime:
    """Convert the raw date in UNIX Epoch to EST/EDT datetime objects.

    Arguments:
      epoch -- The UNIX epoch time to convert.

    Returns:
      A time-aware datetime object representing the corresponding UNIX epoch time.
    """
    return datetime.fromtimestamp(epoch).replace(tzinfo=ZoneInfo("America/New_York"))


def convert_single_quote_sql(text: str) -> str:
    return str.replace(text, "'", "''").rstrip()
