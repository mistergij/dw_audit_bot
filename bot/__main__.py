"""Main entry point for the audit bot."""

import crescent
import hikari

from bot.audit_model import AuditModel
from bot.utils import DISCORD_TOKEN

audit_bot = hikari.GatewayBot(DISCORD_TOKEN)  # pyright: ignore

audit_model = AuditModel()

client = crescent.Client(audit_bot, audit_model)
client.plugins.load_folder("bot.plugins")


def main():
    audit_bot.run()


if __name__ == "__main__":
    main()
