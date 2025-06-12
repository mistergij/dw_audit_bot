"""Plugin that contains all commands for the bot."""
# pyright: reportOptionalMemberAccess=false, reportOptionalSubscript=false
import asyncio
from collections.abc import Sequence
import io
import os

import crescent
import hikari
import pandas as pd

from bot.utils import Plugin

plugin = Plugin()


@plugin.include
@crescent.command(description="Ping the bot to check if it's online.")
async def ping(ctx: crescent.Context) -> None:
    """Returns the bot's latency in milliseconds."""
    current_latency = plugin.app.heartbeat_latency
    await ctx.respond(f"Pong!\nLatency: {current_latency * 1000:.2f} ms")

@plugin.include
@crescent.command(name="audit",
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
    before_raw = crescent.option(
        str,
        name="before",
        description="The start date for the audit. Must be in the format "
                    "YYYY-MM-DD. Defaults to Midnight EST/EDT.",
    )
    after_raw = crescent.option(
        str,
        name="after",
        description="The end date for the audit. Must be in the format "
                    "YYYY-MM-DD. Defaults to Midnight EST/EDT.",
    )
    channel_id = crescent.option(
        int,
        description="The ID of the channel to audit.",
    )
    def __init__(self):
        self.message_iterable: Sequence[hikari.Message] | None = None

    async def get_messages(self) -> Sequence[hikari.Message]:
        before_aware, after_aware = plugin.model.convert_dates(
            self.before_raw,
            self.after_raw
        )
        message_iterable_return = plugin.app.rest.fetch_messages(
            self.channel_id,
            before=before_aware,
            after=after_aware,
        )
        return await message_iterable_return

    async def callback(self, ctx: crescent.Context) -> None:
        try:
            await asyncio.wait_for(self.get_messages(), timeout=2.0)
        except asyncio.TimeoutError:
            await ctx.defer(ephemeral=True)
            self.message_iterable = await self.get_messages()
        if not self.message_iterable:
            await ctx.respond(
                "No messages found in the specified date range."
            )
            return

        csv_dict = {
            "Date": [],
            "DTD Remaining": [],
            "Current Lifestyle": [],
            "Prior Purse": [],
            "Current Purse": [],
            "Payout": [],
            "XP": [],
        }
        for message in self.message_iterable:
            if message.author.mention[2:18] != os.environ["DISCORD_USER_ID"]:
                continue
            message_embed = message.embeds[0]

            if (
                    message_embed.title is not None
                    and "Downtime Activity" in message_embed.title
            ):
                csv_dict["Date"].append(message.timestamp)
                csv_dict["DTD Remaining"].append(
                    message_embed.description.count("◉")
                )

                lifestyle_start = message_embed.description.find(
                    "Current Lifestyle"
                )
                lifestyle_end = message_embed.description[
                    lifestyle_start:
                ].find("\n")
                csv_dict["Current Lifestyle"].append(
                    message_embed.description[
                        lifestyle_start + 21:
                        lifestyle_start + lifestyle_end
                    ]
                )

                prior_purse_start = message_embed.description.find(
                    "Coin Purse"
                )
                prior_purse_end = message_embed.description[
                    prior_purse_start:
                ].find("gp")
                prior_purse_value = message_embed.description[
                        prior_purse_start + 14:
                        prior_purse_start + prior_purse_end
                    ]
                csv_dict["Prior Purse"].append(prior_purse_value)

                current_purse_start = prior_purse_end + 6
                current_purse_end = message_embed.description[
                    current_purse_start:
                ].find("gp")
                current_purse_value = message_embed.description[
                        current_purse_start:
                        current_purse_start + current_purse_end
                    ]
                csv_dict["Current Purse"].append(current_purse_value)

                payout_value: int = (
                        int(current_purse_value)
                        - int(prior_purse_value)
                )
                csv_dict["Payout"].append(payout_value)

        csv_dataframe = pd.DataFrame(csv_dict)
        csv_dataframe_string = csv_dataframe.to_csv(index=False)
        csv_dataframe_file = io.StringIO(csv_dataframe_string)
        csv_dataframe_file_hikari = hikari.Bytes(
            csv_dataframe_file,
            "audit.csv",
            "text/csv",
        )
        await ctx.respond(attachment=csv_dataframe_file_hikari)
