"""Define utility functions and constants for the bot.
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

import os

import crescent
import hikari
from dotenv import find_dotenv, load_dotenv

from bot.audit_model import AuditModel

load_dotenv(find_dotenv(usecwd=True))

Plugin = crescent.Plugin[hikari.GatewayBot, AuditModel]

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")

AVRAE_ID = os.environ.get("AVRAE_ID")
if AVRAE_ID is None:
    raise ValueError("AVRAE_ID environment variable is not set.")
