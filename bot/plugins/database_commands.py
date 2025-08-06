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
import time

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
database_commands = crescent.Group("database")


async def autocomplete_month(
    ctx: crescent.AutocompleteContext,
    option: hikari.AutocompleteInteractionOption,
) -> Sequence[tuple[str, str]]:
    return MONTH_AUTOCOMPLETE


@plugin.include
@crescent.event
async def get_connection(event: hikari.StartingEvent) -> None:
    database.connection = await aiosqlite.connect(MAIN_DATABASE_PATH)
    await database.connection.execute(f'ATTACH DATABASE "{GUILD_DATABASE_PATH}" AS guild;')
    await database.connection.commit()


@plugin.include
@crescent.event
async def close_connection(event: hikari.StoppingEvent) -> None:
    await database.connection.close()


@plugin.include
@database_commands.child
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
@database_commands.child
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


@plugin.include
@database_commands.child
@crescent.command(
    name="audit_guild_downtime",
    description="Intelligently fetch and store data from DTDs",
)
class AuditGuildDTDs:
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
    # TODO: Potentially switch to Snowflake-based time implementation

    async def callback(self, ctx: crescent.Context) -> None:
        aware_date = cvt.convert_date(f"{self.year}-{self.month}-{self.day}")

        try:
            database.earliest_audit = min(aware_date.timestamp(), database.earliest_audit)
        except TypeError:
            database.earliest_audit = aware_date.timestamp()
        try:
            database.latest_audit = max(time.time(), database.latest_audit)
        except TypeError:
            database.latest_audit = time.time()

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            self.channel_id,
            before=cvt.convert_epoch(database.latest_audit),
            after=cvt.convert_epoch(database.earliest_audit),
        )

        async for message in message_iterator:
            try:
                embed = message.embeds[0]
            except Exception as e:
                print(e)
                pass
