import os

import crescent
import dotenv
import hikari

from bot.audit_model import AuditModel
from bot.utils import Plugin

dotenv.load_dotenv()

audit_bot = hikari.GatewayBot(os.environ["DISCORD_TOKEN"])

audit_model = AuditModel()

client = crescent.Client(audit_bot, audit_model)
client.plugins.load_folder("bot.plugins")

audit_bot.run()
