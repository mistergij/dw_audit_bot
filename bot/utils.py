"""Define utility alias for crescent plugins with AuditModel context."""
import crescent
import hikari

from bot.audit_model import AuditModel

Plugin = crescent.Plugin[hikari.GatewayBot, AuditModel]
