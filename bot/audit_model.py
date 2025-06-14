"""Model class used for auditing functionality. This is made available to plugins.
Copyright © 2025 Dnd World

This file is part of Kensa.
Kensa is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

Kensa is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with Kensa. If not, see
<https://www.gnu.org/licenses/>."""

from datetime import datetime
from zoneinfo import ZoneInfo


class AuditModel:
    """Class that defines methods to audit the server's logs."""

    def __init__(self, current_time_zone: ZoneInfo | None = ZoneInfo("America/New_York")) -> None:
        """Initialize the AuditModel with a timezone.

        Arguments:
          current_time_zone -- The timezone to use for date conversions.
        """
        self.current_time_zone = current_time_zone

    def convert_dates(self, after_raw: str) -> datetime:
        """Convert the raw date strings to EST/EDT datetime objects.

        Arguments:
          after_raw -- The audit's end date in the string format YYYY-MM-DD.

        Returns:
          A time-aware datetime object representing the end date of the audit.
        """
        after = datetime.strptime(
            after_raw,
            "%Y-%m-%d",
        ).replace(tzinfo=self.current_time_zone)

        return after
