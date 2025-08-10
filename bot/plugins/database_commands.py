"""Plugin that contains all database commands for the bot.
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

import aiosqlite
import crescent
import hikari

from bot.constants import (
    database,
    Plugin,
    EARLIEST_AUDIT_PATH,
    MAIN_DATABASE_PATH,
)

plugin = Plugin()
database_commands = crescent.Group("database")


@plugin.include
@crescent.event
async def get_connection(event: hikari.StartingEvent) -> None:
    database.connection = await aiosqlite.connect(MAIN_DATABASE_PATH)
    with open(EARLIEST_AUDIT_PATH, "r") as file:
        try:
            database.earliest_audit = float(file.read())
        except ValueError:
            pass


@plugin.include
@crescent.event
async def close_connection(event: hikari.StoppingEvent) -> None:
    await database.connection.close()
    with open(EARLIEST_AUDIT_PATH, "w") as file:
        file.write(str(database.earliest_audit))


@plugin.include
@database_commands.child
@crescent.command(description="Creates the guild DTD database and corresponding tables")
async def create_guild_database(ctx: crescent.Context) -> None:
    await database.connection.execute(
        """CREATE TABLE IF NOT EXISTS guild(
                message_id INTEGER,
                message_timestamp REAL,
                remaining_dtd INTEGER,
                old_purse REAL,
                new_purse REAL,
                lifestyle TEXT,
                injuries TEXT,
                dtd_type TEXT,
                user_id INTEGER,
                user_name TEXT,
                char_name TEXT,
                PRIMARY KEY(message_id DESC)
        );"""
    )
    await ctx.respond("Database created.")


# noinspection PyTypeChecker
@plugin.include
@database_commands.child
@crescent.command(description="Resets latest audit information")
async def reset_latest_audit_info(ctx: crescent.Context) -> None:
    database.earliest_audit = None
    await ctx.respond("Reset Earliest Audit Info!")


@plugin.include
@database_commands.child
@crescent.command(
    name="query_database",
    description="Sends an SQL query to the database for debugging purposes",
)
class QueryDatabase:
    query = crescent.option(str, "The query to pass to the table")

    async def callback(self, ctx: crescent.Context) -> None:
        async with aiosqlite.connect(MAIN_DATABASE_PATH) as c:
            async with c.execute(self.query) as cursor:
                result = await cursor.fetchall()
        await ctx.respond(result)

