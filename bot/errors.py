"""Plugin that contains all audit commands for the bot.
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

from typing import override

import crescent

from bot.constants import Plugin


plugin = Plugin()


class InsufficientPrivilegesError(Exception):
    """Exception raised when a user has insufficient privileges to run a command"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    @override
    def __str__(self) -> str:
        return self.message


class ParsingError(Exception):
    """Exception raised when Kensa cannot parse a message"""

    def __init__(self, guild_id: int, channel_id: int, message_id: int) -> None:
        self.message = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
        super().__init__(self.message)

    @override
    def __str__(self) -> str:
        return self.message


class ArgumentError(Exception):
    """Exception raised when Kensa receives too many arguments for a command"""

    def __init__(self, args_list: list[str]) -> None:
        self.message = f"Issue with arguments provided! Provided Arguments:\n{', '.join(args_list)}"
        super().__init__()

    @override
    def __str__(self) -> str:
        return self.message
