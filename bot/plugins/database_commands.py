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
import polars as pl
import re2

from bot.constants import (
    Plugin,
    GUILD_DATABASE_PATH,
    GUILD_DTD_DICT,
    LATEST_AUDIT_PATH,
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
    with open(LATEST_AUDIT_PATH, "r") as file:
        try:
            database.earliest_audit = float(file.read())
        except ValueError:
            pass


@plugin.include
@crescent.event
async def close_connection(event: hikari.StoppingEvent) -> None:
    await database.connection.close()
    with open(LATEST_AUDIT_PATH, "w") as file:
        file.write(str(database.latest_audit))


@plugin.include
@database_commands.child
@crescent.command(description="Creates the guild DTD database and corresponding tables")
async def create_guild_database(ctx: crescent.Context):
    for dtd in GUILD_DTD_DICT:
        # TODO: Change multiple guild tables into single table in main database
        await database.connection.execute(
            f"""CREATE TABLE IF NOT EXISTS guild.{dtd}(
                    message_id INTEGER,
                    message_timestamp REAL,
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
    def __init__(self):
        self.first_sql_id: int = 0
        self.last_sql_id: int = 0

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

    async def filter_guild_messages(
        self, message_iterator: hikari.LazyIterator[hikari.Message], earliest_break: bool = False
    ) -> pl.DataFrame:
        schema = {
            "Message ID": pl.UInt64,
            "Date": pl.Date,
            "DTD Remaining": pl.UInt8,
            "Old Purse": pl.Float32,
            "New Purse": pl.Float32,
            "Lifestyle": pl.String,
            "Injuries": pl.String,
        }
        csv_df = pl.DataFrame(schema=schema)

        async for message in message_iterator:
            try:
                if (message.timestamp.timestamp() > database.earliest_audit) and earliest_break:
                    self.first_sql_id = message.id
                    break
                if message.timestamp.timestamp() >= database.latest_audit:
                    self.last_sql_id = message.id
                embed = message.embeds[0]
                if "!guild" not in embed.footer.text:
                    continue

                description = embed.description
                footer = embed.footer.text[7:]
                dtd_name = re2.match("\w+", footer)

                if dtd_name not in GUILD_DTD_DICT:
                    continue

                message_id = message.id
                message_timestamp = message.timestamp
                dtd_remaining = description.count("◉")
                old_purse = re2.search(r"\*\*:? (\d+\.\d+)", description)
                new_purse = re2.search(r"-> (\d+\.\d+)", description)
                lifestyle = re2.search(r"le:?\*\*:? ([^\n\r]+)", description)
                injuries = re2.search(r"es:?\*\*:? ([^\n\r]+)", description)

                await database.connection.execute(f"""INSERT INTO guild.{dtd_name} VALUES (
                        {message_id},
                        {message_timestamp.timestamp()},
                        {dtd_remaining},
                        {float(old_purse[0])},
                        {float(new_purse[0])},
                        {"Unknown" if not lifestyle.groups() else lifestyle[0]},
                        {"None" if not injuries.groups() else injuries[0]},
                );""")

                csv_df.vstack(
                    pl.DataFrame(
                        {
                            "Message ID": message_id,
                            "Date": message_timestamp,
                            "DTD Remaining": dtd_remaining,
                            "Old Purse": float(old_purse[0]),
                            "New Purse": float(new_purse[0]),
                            "Lifestyle": "Unknown" if not lifestyle.groups() else lifestyle[0],
                            "Injuries": "None" if not injuries.groups() else injuries[0],
                        }
                    )
                )

            except IndexError:
                pass

        return csv_df

    async def callback(self, ctx: crescent.Context) -> None:
        aware_date = cvt.convert_date(f"{self.year}-{self.month}-{self.day}")

        try:
            database.earliest_audit = min(aware_date.timestamp(), database.earliest_audit)
        except TypeError:
            database.earliest_audit = aware_date.timestamp()

        database.latest_audit = time.time()

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            int(self.channel_id), after=aware_date
        )

        csv_df1 = await self.filter_guild_messages(message_iterator, True)

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            int(self.channel_id), after=database.latest_audit
        )

        csv_df2 = await self.filter_guild_messages(message_iterator)

        database_selection = database.connection.execute(
            f"""SELECT * FROM guild WHERE message_id BETWEEN {self.first_sql_id} AND {self.last_sql_id};"""
        )
