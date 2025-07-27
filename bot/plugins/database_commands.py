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

from collections.abc import Sequence

import aiosqlite
import crescent
import hikari

from bot.constants import (
    Plugin,
    GUILD_DATABASE_PATH,
    GUILD_DTD_LIST,
    MAIN_DATABASE_PATH,
    MONTH_AUTOCOMPLETE,
)
import bot.converters as cvt
from bot.database import Database

plugin = Plugin()
database = Database()
group = crescent.Group("database")


@plugin.include
@crescent.event
async def get_latest_audit(event: hikari.StartingEvent) -> None:
    database.connection = await aiosqlite.connect(MAIN_DATABASE_PATH)
    await database.connection.execute(f'ATTACH DATABASE "{GUILD_DATABASE_PATH}" AS guild;')
    await database.connection.execute(
        f"""CREATE TABLE IF NOT EXISTS timestamps(
            latest_timestamp INTEGER
        );"""
    )
    await database.connection.commit()


@plugin.include
@crescent.event
async def save_latest_audit(event: hikari.StoppingEvent) -> None:
    await database.connection.close()


@plugin.include
@group.child
@crescent.command(description="Creates the guild DTD database and corresponding tables")
async def create_guild_database(ctx: crescent.Context):
    async with aiosqlite.connect(MAIN_DATABASE_PATH) as c:
        for dtd in GUILD_DTD_LIST:
            await c.execute(
                f"""CREATE TABLE IF NOT EXISTS guild.{dtd}(
                        message_id INTEGER,
                        message_timestamp TEXT,
                        remaining_dtd INTEGER,
                        old_purse REAL,
                        new_purse REAL,
                        lifestyle TEXT,
                        injuries TEXT,
                        PRIMARY KEY(message_id DESC)
                );"""
            )
    await ctx.respond("Database created.")


@plugin.include
@group.child
@crescent.command(
    name="query_database",
    description="Sends an SQL query to the database for debugging purposes",
)
class QueryDatabase:
    query = crescent.option(str, "The query to pass to the table")

    async def callback(self, ctx: crescent.Context) -> None:
        async with aiosqlite.connect(MAIN_DATABASE_PATH) as c:
            await c.execute(f'ATTACH DATABASE "{GUILD_DATABASE_PATH}" AS guild;')
            await c.commit()
            async with c.execute(self.query) as cursor:
                result = await cursor.fetchall()
        await ctx.respond(result)


async def autocomplete_month(
    ctx: crescent.AutocompleteContext,
    option: hikari.AutocompleteInteractionOption,
) -> Sequence[tuple[str, str]]:
    return MONTH_AUTOCOMPLETE


@plugin.include
@group.child
@crescent.command(
    name="audit_guild_dtd",
    description="Intelligently fetch and store data from DTDs",
)
class WriteTables:
    channel_id = crescent.option(
        str,
        name="channel",
        description="The ID of the channel to audit.",
    )
    year = crescent.option(
        str,
        description="The year after which to audit.",
    ).convert(cvt.to_int)
    month = crescent.option(str, description="The month after which to audit.", autocomplete=autocomplete_month)
    day = crescent.option(int, description="The day after which to audit.").convert(cvt.convert_day)

    async def callback(self, ctx: crescent.Context) -> None:
        aware_date = cvt.convert_date(f"{self.year}-{self.month}-{self.day}")
        message_iterator = plugin.app.rest.fetch_messages(self.channel_id, aware_date)
