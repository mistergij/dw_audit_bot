"""Define utility variables, functions, and classes for the bot."""
import dataclasses
from datetime import datetime
from zoneinfo import ZoneInfo

import crescent
import hikari

Plugin = crescent.Plugin[hikari.GatewayBot, None]


@dataclasses.dataclass
class RunAudit:
    """Class that defines methods to audit the server's logs."""
    before_raw: str = "2025-01-02"
    after_raw: str = "2025-01-01"
    current_time_zone: ZoneInfo = ZoneInfo("America/New_York")

    def convert_dates(self) -> tuple[datetime, datetime]:
        """Convert the raw date strings to EST/EDT datetime objects.

        Arguments:
          before_raw -- The audit's start date in the format YYYY-MM-DD.
          after_raw -- The audit's end date in the format YYYY-MM-DD.

        Returns:
          A tuple containing two datetime objects: (before, after).
        """
        before = datetime.strptime(
            self.before_raw,
            "%Y-%m-%d",
        ).replace(tzinfo=self.current_time_zone)
        after = datetime.strptime(
            self.after_raw,
            "%Y-%m-%d",
        ).replace(tzinfo=self.current_time_zone)

        return before, after

    def filter_messages(
            self,
            messages: list[hikari.Message],
            user: hikari.User,
    ) -> list[hikari.Message]:
        for index, message in enumerate(messages):
            if message.author != user:
                messages.pop(index)
            
        return messages
