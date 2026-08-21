"""SendLayer Python SDK."""

from typing import Any, Dict, Optional

from .base import BaseClient
from .email import Emails
from .webhooks import Webhooks
from .events import Events
from .exceptions import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerNotFoundError,
    SendLayerRateLimitError,
    SendLayerValidationError,
    SendLayerInternalServerError,
)


class SendLayer:
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the SDK.

        Args:
            api_key: Your SendLayer API key.
            config: Optional settings forwarded to the underlying client --
                ``timeout`` (seconds, default 30), ``attachmentURLTimeout``
                (milliseconds), and ``requests`` for extra session options.
        """
        client = BaseClient(api_key, config)
        self.Emails = Emails(client)
        self.Webhooks = Webhooks(client)
        self.Events = Events(client)


__all__ = [
    "SendLayer",
    "SendLayerError",
    "SendLayerAPIError",
    "SendLayerAuthenticationError",
    "SendLayerNotFoundError",
    "SendLayerRateLimitError",
    "SendLayerValidationError",
    "SendLayerInternalServerError",
]
