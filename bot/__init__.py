"""Defines optimizations for event loop and defines the main entry point for Kensa.
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

import asyncio
import os

import crescent
import hikari

from bot.constants import DISCORD_TOKEN, ERROR_LOG_PATH

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

audit_bot = hikari.GatewayBot(
    DISCORD_TOKEN,
    logs={
        "version": 1,
        "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s %(message)s"}},
        "handlers": {
            "default": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "filename": ERROR_LOG_PATH,
                "encoding": "utf-8",
            },
            "output": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
                "formatter": "standard",
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default", "output"],
                "propagate": False,
                "level": "DEBUG",
            }
        },
    },
)

client = crescent.Client(audit_bot)
client.plugins.load_folder("bot.plugins")


def main():
    try:
        audit_bot.run()
    finally:
        print("Bot Stopped Successfully!")
