"""Exceptions for the Taiwan Real-time Earthquake Monitoring."""

from homeassistant import exceptions


class AccountInvalid(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class RegionInvalid(exceptions.HomeAssistantError):
    """Error to indicate we not found."""


class UnknownError(exceptions.HomeAssistantError):
    """Represents an unknown error."""


class WebSocketClosure(exceptions.HomeAssistantError):
    """Represents a websocket closed signal."""
