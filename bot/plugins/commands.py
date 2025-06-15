"""Plugin that contains all commands for the bot.
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

# pyright: reportOptionalMemberAccess=false, reportOptionalSubscript=false
from collections.abc import Sequence
import io

import crescent
import hikari
import polars as pl
import re2

from bot.utils import AVRAE_ID, Plugin

plugin = Plugin()


@plugin.include
@crescent.command(
    description="Ping the bot to check if it's online.",
)
async def ping(ctx: crescent.Context) -> None:
    """Returns the bot's latency in milliseconds."""
    current_latency = plugin.app.heartbeat_latency
    await ctx.respond(f"Pong!\nLatency: {current_latency * 1000:.2f} ms")


@plugin.include
@crescent.command(
    name="audit_dtd",
    description="Performs a new audit of the server's logs.",
)
class AuditCommand:
    """Command to perform an audit of the server's logs.

    Arguments:
      before_raw -- The start date for the audit in the format YYYY-MM-DD.
                      Defaults to Midnight EST/EDT.
      after_raw -- The end date for the audit in the format YYYY-MM-DD.
                      Defaults to Midnight EST/EDT.
      channel_id -- The ID of the channel to audit.
    """

    channel_id = crescent.option(
        str,
        name="channel",
        description="The ID of the channel to audit.",
    )
    user_id = crescent.option(
        str,
        name="user",
        description="The ID of the user to audit.",
    )
    after_raw = crescent.option(
        str,
        name="after",
        description="The end date for the audit. Must be in the format YYYY-MM-DD. Defaults to Midnight EST/EDT.",
    )

    def __init__(self):
        self.message_iterator: hikari.LazyIterator[hikari.Message] | None = None
        self.message_iterable: Sequence[hikari.Message] | None = None

    async def get_messages(self) -> None:
        """Fetches messages from the specified channel within the date range."""
        after_aware = plugin.model.convert_dates(self.after_raw)
        message_iterable_return = plugin.app.rest.fetch_messages(
            int(self.channel_id),
            after=after_aware,
        )
        self.message_iterator = message_iterable_return

    async def callback(self, ctx: crescent.Context) -> None:
        """Callback for the audit command."""
        await ctx.defer()
        await ctx.respond(
            "Fetching messages, this may take a while...",
            ephemeral=True,
        )
        await self.get_messages()

        if self.message_iterator is not None:
            self.message_iterable = await self.message_iterator
        else:
            await ctx.respond("No messages found in the specified date range.")
            return

        schema = {
            "Date": pl.Date,
            "DTD Remaining": pl.UInt8,
            "Current Lifestyle": pl.String,
            "Prior Purse": pl.Float32,
            "Current Purse": pl.Float32,
            "Payout": pl.Float32,
        }
        csv_df = pl.DataFrame(schema)

        for message in self.message_iterable:
            if message.author.mention != AVRAE_ID:
                continue
            try:
                message_embed = message.embeds[0]
            except IndexError:
                continue

            player_id = re2.search(message_embed.description, r".+<@(\d+)").group(0)

            if (
                message_embed.title is not None
                and "Downtime Activity" in message_embed.title
                and player_id == self.user_id
            ):
                prior_purse = round(
                    float(
                        re2.search(message_embed.description, r"(?:Purse|Automated\))[*]{2}:?\s([0-9.]+)gp").group(0)
                    ),
                    2,
                )
                current_purse = round(float(re2.search(message_embed.description, r"-> ([0-9.]+)gp").group(0)), 2)

                csv_df.vstack(
                    pl.DataFrame(
                        {
                            "Date": [message.timestamp.date()],
                            "DTD Remaining": [message_embed.description.count("◉")],
                            "Current Lifestyle": [
                                re2.search(
                                    message_embed.description,
                                    r".+Lifestyle:?[*]{2}:? (\w+)",
                                ).group(0)
                            ],
                            "Prior Purse": [
                                prior_purse,
                            ],
                            "Current Purse": [
                                current_purse,
                            ],
                            "Payout": [
                                round(
                                    current_purse - prior_purse,
                                    2,
                                )
                            ],
                        },
                        schema=schema,
                    ),
                    in_place=True,
                )

        csv_df_string = csv_df.write_csv()
        csv_df_file = io.StringIO(csv_df_string)
        csv_df_file_hikari = hikari.Bytes(
            csv_df_file,
            "audit.csv",
            "text/csv",
        )
        await ctx.respond(attachment=csv_df_file_hikari)
