"""Plugin that contains all commands for the bot."""
import asyncio
from collections.abc import Sequence
import os

import crescent
import hikari

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
    message_iterable = None

    async def get_messages(self) -> Sequence[hikari.Message]:
        before_aware, after_aware = plugin.model.convert_dates(
            self.before_raw,
            self.after_raw
        )
        message_iterable = plugin.app.rest.fetch_messages(
            self.channel_id,
            before=before_aware,
            after=after_aware,
        )
        return await message_iterable

    async def callback(self, ctx: crescent.Context) -> None:
        if not plugin.model.avrae:
            plugin.model.avrae = plugin.app.cache.get_user(
                int(os.environ["AVRAE_ID"])
            )

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
