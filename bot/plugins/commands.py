import crescent

from bot.utils import Plugin

plugin = Plugin()


@plugin.include
@crescent.command(description="Ping the bot to check if it's online.")
async def ping(ctx: crescent.Context) -> None:
    """Returns the bot's latency in milliseconds."""
    current_latency = plugin.app.heartbeat_latency
    await ctx.respond(f"Pong!\nLatency: {current_latency * 1000:.2f} ms")

@plugin.include
@crescent.command(name="audit", description="Performs a new audit of the server's logs.")
class AuditCommand:
    before = crescent.option(
        str, 
        description="The start date for the audit. Must be in the format YYYY-MM-DD. Defaults to Midnight EST/EDT.",
    )
    after = crescent.option(
        str, 
        description="The end date for the audit. Must be in the format YYYY-MM-DD. Defaults to Midnight EST/EDT.",
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer()
