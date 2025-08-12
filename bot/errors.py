from typing import override

import crescent

from bot import client
from bot.constants import Plugin


plugin = Plugin()


class InsufficientPrivilegesError(Exception):
    """Exception raised when a user has insufficient privileges to run a command"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    @override
    def __str__(self):
        return self.message


@plugin.include
@crescent.catch_command(InsufficientPrivilegesError)
async def catch_permission_error(exc: InsufficientPrivilegesError, ctx: crescent.Context) -> None:
    await ctx.respond(exc)
