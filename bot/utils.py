"""Define utility functions and constants for the bot."""

import os

import crescent
import hikari
from dotenv import find_dotenv, load_dotenv

from bot.audit_model import AuditModel

load_dotenv(find_dotenv(usecwd=True))

Plugin = crescent.Plugin[hikari.GatewayBot, AuditModel]

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")

AVRAE_ID = os.environ.get("AVRAE_ID")
if AVRAE_ID is None:
    raise ValueError("AVRAE_ID environment variable is not set.")
