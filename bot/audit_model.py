"""Model class used for auditing functionality. This is made available to plugins."""
from datetime import datetime
from zoneinfo import ZoneInfo

class AuditModel:
    """Class that defines methods to audit the server's logs."""
    def __init__(
            self,
            current_time_zone: ZoneInfo | None = ZoneInfo("America/New_York")
    ) -> None:
        """Initialize the AuditModel with a timezone.

        Arguments:
          current_time_zone -- The timezone to use for date conversions.
        """
        self.current_time_zone = current_time_zone

    def convert_dates(self,
                      before_raw: str,
                      after_raw: str) -> tuple[datetime, datetime]:
        """Convert the raw date strings to EST/EDT datetime objects.

        Arguments:
          before_raw -- The audit's start date in the format YYYY-MM-DD.
          after_raw -- The audit's end date in the format YYYY-MM-DD.

        Returns:
          A tuple containing two datetime objects: (before, after).
        """
        before = datetime.strptime(
            before_raw,
            "%Y-%m-%d",
        ).replace(tzinfo=self.current_time_zone)
        after = datetime.strptime(
            after_raw,
            "%Y-%m-%d",
        ).replace(tzinfo=self.current_time_zone)

        return before, after
