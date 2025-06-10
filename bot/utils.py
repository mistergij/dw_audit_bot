"""Define utility variables, functions, and classes for the bot."""
import crescent
import hikari

from bot.audit_model import AuditModel

Plugin = crescent.Plugin[hikari.GatewayBot, AuditModel]
