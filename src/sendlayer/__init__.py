"""SendLayer Python SDK."""

from .base import BaseClient
from .email import NewEmail
from .webhooks import Webhooks
from .events import Events
from .exceptions import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerValidationError
)


__version__ = "1.0.0"
__all__ = [
    "BaseClient",
    "NewEmail",
    "Webhooks",
    "Events",
    "SendLayerError",
    "SendLayerAPIError",
    "SendLayerAuthenticationError",
    "SendLayerValidationError"
] 