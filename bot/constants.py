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

from bot.database import Database


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
EARLIEST_AUDIT_PATH = os.path.join(os.getcwd(), "bot", "resources", "earliest_audit.txt")
GUILD_DTD_DICT = {
    "alchem",
    0,
    "arcana",
    1,
    "armam",
    2,
    "assassinate",
    3,
    "crime",
    4,
    "cult",
    5,
    "explore",
    6,
    "farm",
    7,
    "med",
    8,
    "merc",
    9,
    "merchant",
    10,
    "patrol",
    11,
    "research",
    12,
    "scribe",
    13,
    "showtime",
    14,
    "works",
    15,
    "healer",
    16,
    "assasinate",
    17,
}
GUILD_DTD_CHOICES = [
    ("alchem", "alchem"),
    ("arcana", "arcana"),
    ("armam", "armam"),
    ("assassinate", "assassinate"),
    ("crime", "crime"),
    ("cult", "cult"),
    ("explore", "explore"),
    ("farm", "farm"),
    ("med", "med"),
    ("merc", "merc"),
    ("merchant", "merchant"),
    ("patrol", "patrol"),
    ("research", "research"),
    ("scribe", "scribe"),
    ("showtime", "showtime"),
    ("works", "works"),
    ("healer", "healer"),
]
MONTH_CHOICES = [
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

CHANNEL_CHOICES = [
    ("dtd-automated-log", "579777361117970465"),
    ("lifestyle-log", "586471153141284866"),
]

database = Database()
