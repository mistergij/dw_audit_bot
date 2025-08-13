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

import io
import time
from datetime import datetime

import aiosqlite
import crescent
import hikari
import numpy as np
import polars as pl
import re2
import sys

from bot.constants import (
    CHANNEL_CHOICES,
    database,
    Plugin,
    GUILD_DTD_CHOICES,
    GUILD_ID,
    MAIN_DATABASE_PATH,
    MONTH_CHOICES,
)
from bot.errors import ArgumentError, ParsingError
import bot.converters as cvt

plugin = Plugin()
audit_commands = crescent.Group("audit")


@plugin.include
@crescent.command(description="Ping the bot to check if it's online.")
async def ping(ctx: crescent.Context) -> None:
    """Returns the bot's latency in milliseconds."""
    current_latency = plugin.app.heartbeat_latency
    await ctx.respond(f"Pong!\nLatency: {current_latency * 1000:.2f} ms")


@plugin.include
@audit_commands.child
@crescent.command(name="get_message", description="Performs a new audit of the server's logs.")
class GetMessage:
    channel_id = crescent.option(
        str, description="The ID of the message's channel.", choices=[("#dtd-automated-log", "579777361117970465")]
    )
    message_id = crescent.option(
        str,
        description="The ID of the message.",
    )
    content_type = crescent.option(
        int, description="The type of content you want to return", choices=[("message", 0), ("embed", 1)]
    )

    async def callback(self, ctx: crescent.Context):
        message = await plugin.app.rest.fetch_message(int(self.channel_id), int(self.message_id))
        if self.content_type == 0:
            await ctx.respond(message)
        else:
            embed = message.embeds[0]
            await ctx.respond(
                f"**Title:** `{embed.title}`\n"
                f"**Description:** ```{embed.description}```\n"
                f"**Fields:** {''.join([f'\nField {i}: \n```{value.name}\n{value.value}```' for i, value in enumerate(embed.fields)])}\n"
                f"**Footer:** `{embed.footer}`\n"
            )


@plugin.include
@audit_commands.child
@crescent.command(
    name="full",
    description="Intelligently fetch and store data from DTDs",
)
class AuditDTDs:
    def __init__(self):
        self.first_sql_id: int = sys.maxsize
        self.schema = {
            "message_id": pl.UInt64,
            "message_timestamp": pl.Float64,
            "remaining_dtd": pl.UInt8,
            "old_purse": pl.Float32,
            "new_purse": pl.Float32,
            "lifestyle": pl.String,
            "injuries": pl.String,
            "dtd_type": pl.String,
            "user_id": pl.UInt64,
            "user_name": pl.String,
            "char_name": pl.String,
        }

    channel_id = crescent.option(
        str,
        name="channel",
        description="The ID of the channel to audit.",
        choices=CHANNEL_CHOICES,
    ).convert(cvt.to_int)
    year = crescent.option(
        str,
        description="The year after which to audit.",
    ).convert(cvt.to_int)
    month = crescent.option(str, description="The month after which to audit.", choices=MONTH_CHOICES)
    day = crescent.option(int, description="The day after which to audit.").convert(cvt.convert_day)
    char_name = crescent.option(str, description="(Optional) The name of the character to audit.", default="")
    user_id = crescent.option(str, description="(Optional) The ID of the User to audit.", default="").convert(
        cvt.to_int
    )
    dtd_type = crescent.option(
        str, description="(Optional) The DTD type you wish to audit.", default="", choices=GUILD_DTD_CHOICES
    )

    async def update_tables(
        self, message_iterator: hikari.LazyIterator[hikari.Message], earliest_break: bool = False
    ) -> None:
        async for message in message_iterator:
            try:
                if (
                    (database.earliest_audit is not None)
                    and (message.timestamp.timestamp() > database.earliest_audit)
                    and earliest_break
                ):
                    self.first_sql_id = message.id
                    break

                embed = message.embeds[0]
                description = embed.description
                if (description is None) or ("Insufficient downtime" in description):
                    continue
                for field in embed.fields:
                    description += f"\n{field.name}\n{field.value}"

                footer = embed.footer.text

                if embed.title is None:
                    continue
                elif "High-Risk Work" in embed.title:
                    to_audit = "hrw"
                    dtd_type = "N/A"
                elif footer is None:
                    continue
                elif "!guild" in footer:
                    to_audit = "guild"
                    dtd_type = re2.match(r"\w+", footer[7:])[0].replace("assasinate", "assassinate")
                elif "!business" in footer:
                    to_audit = "business"
                    dtd_type = re2.search(r"Business Category:?\*\*:? ([^\n\r]+)", description)[1]
                elif "!ptw" in footer:
                    to_audit = "ptw"
                    dtd_type = "N/A"
                else:
                    continue

                message_id = message.id
                message_timestamp = message.timestamp
                dtd_remaining = description.count("◉")
                old_purse = re2.search(r"\*\*:? (\d+\.\d+)", description)
                new_purse = re2.search(r"-> (\d+\.\d+)", description)
                lifestyle = re2.search(r"Lifestyle:?\*\*:? ([^\n\r]+)", description)
                injuries = re2.search(r"Injuries:?\*\*:? ([^\n\r]+)", description)
                user_id_and_name = re2.search(r"Player:?\*\*:? <@(\d+)> `([^`\n\r]+)", description)
                char_name = re2.search(r"Character:?\*\*:? ([^\n]+)", description)

                try:
                    await database.connection.execute(
                        f"INSERT INTO {to_audit} VALUES (?,?,?,?,?,?,?,?,?,?,?);",
                        (
                            message_id,
                            message_timestamp.timestamp(),
                            dtd_remaining,
                            0 if old_purse is None else float(old_purse[1]),
                            0 if new_purse is None else float(new_purse[1]),
                            "Unknown" if lifestyle is None else lifestyle[1],
                            "None" if injuries is None else injuries[1],
                            dtd_type,
                            0 if user_id_and_name is None else user_id_and_name[1],
                            "Unknown" if user_id_and_name is None else user_id_and_name[2],
                            re2.sub(r"\s\(\d+\)", "", char_name[1]),
                        ),
                    )
                    await database.connection.commit()
                except aiosqlite.IntegrityError:
                    continue
                except TypeError:
                    raise ParsingError

            # Handles if message does not have an Embed or if Embed doesn't have a Footer
            except (IndexError, AttributeError):
                pass
            except TypeError:
                raise ParsingError

    async def filter_tables(self, aware_date: datetime) -> pl.DataFrame:
        options_list = list(filter(None, map(str.strip, [self.dtd_type, str(self.user_id), self.char_name])))
        num_options = len(options_list)
        if num_options > 1:
            raise ArgumentError(options_list)
        try:
            search_str = options_list[0]
        except IndexError:
            raise ArgumentError(options_list)

        print(search_str)
        return pl.read_database(
            "SELECT raw_all.* from raw_all INNER JOIN filtered_all ON raw_all.message_id = filtered_all.rowid WHERE filtered_all MATCH :search AND raw_all.message_timestamp > :timestamp",
            database.engine,
            execute_options={
                "parameters": {
                    "search": search_str,
                    "timestamp": aware_date.timestamp()
                }
            },
        )

    async def callback(self, ctx: crescent.Context) -> None:
        start = time.perf_counter()
        await ctx.defer()
        aware_date = cvt.convert_date(f"{self.year}-{self.month}-{self.day}")

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            self.channel_id, after=aware_date
        )

        # Find messages not yet in database
        await self.update_tables(message_iterator, True)

        # Update variables to reflect new entries in database
        try:
            database.earliest_audit = min(aware_date.timestamp(), database.earliest_audit)
        except TypeError:
            database.earliest_audit = aware_date.timestamp()

        # Create cursor to find most recent timestamp in database
        cursor = await database.connection.execute(
            "SELECT message_timestamp FROM raw_all ORDER BY message_timestamp DESC LIMIT 1"
        )
        latest_sql_timestamp = await cursor.fetchone()

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            self.channel_id,
            after=cvt.convert_epoch(float(latest_sql_timestamp[0])),
        )
        await cursor.close()

        # Find messages sent after SQL Database was last updated
        await self.update_tables(message_iterator)

        # Fetch all messages stored in database

        sql_df = await self.filter_tables(aware_date)

        time_column = sql_df.select(
            pl.from_epoch("message_timestamp", time_unit="s")
            .dt.convert_time_zone("America/New_York")
            .cast(pl.String)
            .replace("T", "")
        ).to_series(0)
        sql_df.replace_column(1, time_column)
        output_string = sql_df.write_csv()
        output_file = io.StringIO(output_string)
        await ctx.respond(
            attachment=hikari.Bytes(
                output_file,
                "audit.csv",
                "text/csv",
            )
        )
        end = time.perf_counter()
        elapsed = end - start
        print(f"/audit guild executed in {elapsed:.4f} seconds.")


@plugin.include
@crescent.catch_command(ArgumentError)
async def catch_argument_error(exc: ArgumentError, ctx: crescent.Context) -> None:
    await ctx.respond(exc)


@plugin.include
@crescent.catch_command(ParsingError)
async def catch_parsing_error(exc: ParsingError, ctx: crescent.Context) -> None:
    await ctx.respond(f"Unexpected error! Please provide the following link to <@657638997941813258>:\n{exc}")
