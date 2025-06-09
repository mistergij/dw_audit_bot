"""Define Plugin type alias for crescent plugins."""
import crescent
import hikari

Plugin = crescent.Plugin[hikari.GatewayBot, None]
