from typing import Any, Dict, List, Optional


class SendLayerError(Exception):
    """Base exception for SendLayer SDK.

    Every SendLayer exception carries the same attributes so callers can
    inspect them without first checking which subclass they caught:

    - ``message``     the human-readable message
    - ``status_code`` HTTP status of the response, or None for local errors
    - ``response``    decoded response body, or {} when unavailable
    - ``errors``      raw SendLayer ``Errors`` entries, each with the API's
                      numeric ``Code`` and ``Message``; empty for local errors
                      and for responses that aren't in that shape
    """

    def __init__(
        self,
        message: str = "",
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = {} if response is None else response
        self.errors = [] if errors is None else errors
        super().__init__(message)

    @property
    def codes(self) -> List[Any]:
        """Numeric SendLayer error codes carried by this exception.

        Convenience for ``if 14 in err.codes:`` style branching. See
        https://developers.sendlayer.com/api-reference/error-codes
        """
        return [e["Code"] for e in self.errors if isinstance(e, dict) and "Code" in e]


class SendLayerAPIError(SendLayerError):
    """Exception raised for API errors not covered by a more specific type."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message, status_code=status_code, response=response, errors=errors)
        # Preserve the historical "API Error <status>: <message>" string form.
        self.args = (f"API Error {status_code}: {message}",)


class SendLayerAuthenticationError(SendLayerError):
    """Exception raised for authentication errors."""


class SendLayerNotFoundError(SendLayerError):
    """Exception raised for not found errors."""


class SendLayerRateLimitError(SendLayerError):
    """Exception raised for rate limit errors."""


class SendLayerValidationError(SendLayerError):
    """Exception raised for validation errors."""


class SendLayerInternalServerError(SendLayerError):
    """Exception raised for internal server errors."""
