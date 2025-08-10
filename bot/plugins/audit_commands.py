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
import polars as pl
import re2
import sys

from bot.constants import (
    CHANNEL_CHOICES,
    database,
    Plugin,
    GUILD_DTD_CHOICES,
    GUILD_DTD_DICT,
    GUILD_ID,
    MAIN_DATABASE_PATH,
    MONTH_CHOICES,
)
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
    char_name = crescent.option(str, description="(Optional) The name of the character to audit.", default="").convert(
        cvt.convert_single_quote_sql
    )
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

                if embed.footer.text is None:
                    continue
                if "!guild" in embed.footer.text:
                    to_audit = "guild"
                    dtd_type = re2.match(r"\w+", embed.footer.text[7:])[0].replace("assasinate", "assassinate")
                elif "!business" in embed.footer.text:
                    to_audit = "business"
                    print(description)
                    dtd_type = re2.search(r"Business Category:?\*\*:? ([^\n\r]+)", description)[1]
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
                    await database.connection.execute(f"""INSERT INTO {to_audit} VALUES (
                                                      {message_id},
                                                      {message_timestamp.timestamp()},
                                                      {dtd_remaining},
                                                      {0 if old_purse is None else float(old_purse[1])},
                                                      {0 if new_purse is None else float(new_purse[1])},
                                                      '{"Unknown" if lifestyle is None else lifestyle[1]}',
                                                      '{"None" if injuries is None else injuries[1]}',
                                                      '{dtd_type}',
                                                      {0 if user_id_and_name is None else user_id_and_name[1]},
                                                      '{"Unknown" if user_id_and_name is None else cvt.convert_single_quote_sql(user_id_and_name[2])}',
                                                      '{cvt.convert_single_quote_sql(re2.sub(r"\s\(\d+\)", "", char_name[1]))}'
                                                      );""")
                    await database.connection.execute(
                        f"""INSERT INTO search_{to_audit} VALUES(
                        {message_id},
                        '{dtd_type}',
                        {0 if user_id_and_name is None else user_id_and_name[1]},
                        '{cvt.convert_single_quote_sql(char_name[1])}'
                        );"""
                    )
                    await database.connection.commit()
                except aiosqlite.IntegrityError:
                    continue
                except TypeError:
                    print(
                        f"Unexpected Error! Message Link: https://discord.com/channels/{GUILD_ID}/{self.channel_id}/{message.id}"
                    )

            # Handles if message does not have an Embed or if Embed doesn't have a Footer
            except (IndexError, AttributeError):
                pass

    def create_query(self) -> str:
        options = [self.char_name, self.user_id, self.dtd_type]
        not_options = [not option for option in options]
        option_names = ["char_name", "user_id", "dtd_type"]
        prior_query = False
        return_string = ""
        for idx, option in enumerate(options):
            if not option:
                continue
            if not prior_query:
                return_string += f" WHERE {option_names[idx]} MATCH '\"{option_names[idx]}\" : {option}'"
            if ((idx == 0) and (not not_options[1] or not not_options[2])) or ((idx == 1) and not not_options[2]):
                return_string += " AND "

        return return_string

    async def filter_tables(self, aware_date: datetime) -> pl.DataFrame:
        return pl.read_database_uri(
            f"SELECT * FROM guild WHERE message_timestamp > {aware_date.timestamp()} AND message_id IN (SELECT message_id FROM search_guild{self.create_query()}) UNION SELECT * FROM business WHERE message_timestamp > {aware_date.timestamp()} AND message_id IN (SELECT message_id FROM search_business{self.create_query()})",
            "sqlite:///" + MAIN_DATABASE_PATH,
            schema_overrides=self.schema,
        )

    async def callback(self, ctx: crescent.Context) -> None:
        start = time.perf_counter()
        await ctx.defer()
        aware_date = cvt.convert_date(f"{self.year}-{self.month}-{self.day}")

        message_iterator: hikari.LazyIterator[hikari.Message] = plugin.app.rest.fetch_messages(
            self.channel_id, after=aware_date
        )

        # Create virtual table for searching
        await database.connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS search_guild USING FTS5(message_id, dtd_type, user_id, char_name);"
        )
        await database.connection.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS search_business USING FTS5(message_id, dtd_type, user_id, char_name);"
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
            "SELECT message_timestamp FROM (SELECT message_timestamp FROM guild UNION SELECT message_timestamp FROM business) ORDER BY message_timestamp DESC LIMIT 1"
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
