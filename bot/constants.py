"""Defines various constants for the bot.
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


load_dotenv(find_dotenv(usecwd=True))

Plugin = crescent.Plugin[hikari.GatewayBot, None]

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")

AVRAE_ID = os.environ.get("AVRAE_ID")
if AVRAE_ID is None:
    raise ValueError("AVRAE_ID environment variable is not set.")

GUILD_ID = os.environ.get("GUILD_ID")
if GUILD_ID is None:
    raise ValueError("GUILD_ID environment variable is not set.")

MAIN_DATABASE_PATH = os.path.join(os.getcwd(), "bot", "resources", "database.sqlite")
GUILD_DATABASE_PATH = os.path.join(os.getcwd(), "bot", "resources", "guild.sqlite")
LATEST_AUDIT_PATH = os.path.join(os.getcwd(), "bot", "resources", "latest_audit.txt")
GUILD_DTD_LIST = [
    "alchem",
    "arcana",
    "armam",
    "assassinate",
    "crime",
    "cult",
    "explore",
    "farm",
    "med",
    "merc",
    "merchant",
    "patrol",
    "research",
    "scribe",
    "showtime",
    "works",
    "healer",
]
MONTH_AUTOCOMPLETE = [
    ("January", "01"),
    ("February", "02"),
    ("March", "03"),
    ("April", "04"),
    ("May", "05"),
    ("June", "06"),
    ("July", "07"),
    ("August", "08"),
    ("September", "09"),
    ("October", "10"),
    ("November", "11"),
    ("December", "12"),
]

DAY_DICTIONARY = {
    "01": 31,
    "02": 28,
    "03": 31,
    "04": 30,
    "05": 31,
    "06": 30,
    "07": 31,
    "08": 31,
    "09": 30,
    "10": 31,
    "11": 30,
    "12": 31,
}
