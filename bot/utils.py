"""Define utility variables, functions, and classes for the bot."""
import dataclasses
import datetime

import crescent
import hikari

Plugin = crescent.Plugin[hikari.GatewayBot, None]


@dataclasses.dataclass
class RunAudit:
    """Class that defines methods to run an audit of the server's logs."""
    before_raw: str
    after_raw: str

    def convert_dates(self) -> tuple[datetime.datetime, datetime.datetime]:
        """Convert the raw date strings to datetime objects.

        Arguments:
            before_raw -- The start date for the audit in the format YYYY-MM-DD.
            after_raw -- The end date for the audit in the format YYYY-MM-DD.

        Returns:
            A tuple containing two datetime objects: (before, after).
        """
        before = datetime.datetime.strptime(self.before_raw, "%Y-%m-%d")
        after = datetime.datetime.strptime(self.after_raw, "%Y-%m-%d")
        return before, after
