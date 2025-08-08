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

import crescent

from bot.constants import Plugin

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
                f"**Fields:** {''.join([f'\nField {i}: \n```{value}```' for i, value in enumerate(embed.fields)])}\n"
                f"**Footer:** `{embed.footer}`\n"
            )
