"""Exceptions for the Taiwan Real-time Earthquake Monitoring."""

from homeassistant import exceptions


class AccountInvalid(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class RegionInvalid(exceptions.HomeAssistantError):
    """Error to indicate we not found."""


class AuthorizationFailed(exceptions.HomeAssistantError):
    """Represents an authorization failure."""


class AuthorizationLimit(exceptions.HomeAssistantError):
    """Represents an authorization limit."""


class WebSocketClosure(exceptions.HomeAssistantError):
    """Represents a websocket closed signal."""


class MembershipExpired(exceptions.HomeAssistantError):
    """Represents a membership expired."""


class RateLimitExceeded(exceptions.HomeAssistantError):
    """Represents a rate limit exceeded."""
