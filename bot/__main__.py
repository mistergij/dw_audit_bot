import os

import crescent
import dotenv
import hikari

from utils import RunAudit

dotenv.load_dotenv()

audit_bot = hikari.GatewayBot(os.environ["DISCORD_TOKEN"])

client = crescent.Client(audit_bot)
client.plugins.load_folder("bot.plugins")

audit_bot.run()