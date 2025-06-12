"""Main entry point for the audit bot."""
import crescent
import dotenv
import hikari

from bot.audit_model import AuditModel
from bot.utils import DISCORD_TOKEN

dotenv.load_dotenv()

audit_bot = hikari.GatewayBot(DISCORD_TOKEN) # pyright: ignore

audit_model = AuditModel()

client = crescent.Client(audit_bot, audit_model)
client.plugins.load_folder("bot.plugins")

audit_bot.run()
