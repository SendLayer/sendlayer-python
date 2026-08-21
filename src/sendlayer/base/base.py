import requests
from typing import Any, Dict, List, Optional
from ..exceptions import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerValidationError,
    SendLayerNotFoundError,
    SendLayerRateLimitError,
    SendLayerInternalServerError
)

class BaseClient:
    """Base client for SendLayer API interactions."""

    #: Seconds to wait for the API before giving up. requests defaults to
    #: no timeout, which lets a hung connection block forever.
    DEFAULT_TIMEOUT = 30
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base client with API key and optional configuration."""
        self.api_key = api_key
        self.base_url = "https://console.sendlayer.com/api/v1"
        
        # Set default config values
        config = config or {}
        self.attachment_url_timeout = config.get('attachmentURLTimeout', 30000)
        
        # Configure session
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # requests.Session has no honoured `timeout` attribute -- Session.request()
        # only reads the per-request keyword -- so hold it here and pass it on
        # every call instead.
        self.timeout = config.get('timeout', self.DEFAULT_TIMEOUT)

        # Apply any additional session configuration from config
        if 'requests' in config:
            requests_config = config['requests']
            if 'timeout' in requests_config:
                self.timeout = requests_config['timeout']
            if 'headers' in requests_config:
                self._session.headers.update(requests_config['headers'])

    # HTTP status -> (exception class, fallback message used when the API
    # response carries no message of its own).
    _ERROR_MAP = {
        400: (SendLayerValidationError, "Invalid request parameters"),
        401: (SendLayerAuthenticationError, "Invalid API key"),
        404: (SendLayerNotFoundError, "Resource not found"),
        422: (SendLayerValidationError, "Unprocessable Entity"),
        429: (SendLayerRateLimitError, "Rate limit exceeded"),
        500: (SendLayerInternalServerError, "Internal server error"),
    }

    @staticmethod
    def _parse_body(response: "requests.Response") -> Dict[str, Any]:
        """Decode an error response body.

        Falls back to the HTTP reason phrase when the body isn't JSON, so an
        HTML error page from a proxy still produces a usable message instead of
        raising a JSONDecodeError out of the SDK.
        """
        try:
            data = response.json()
        except ValueError:
            data = None

        if isinstance(data, dict):
            return data

        return {"Error": response.reason or "Unknown error"}

    @staticmethod
    def _extract_errors(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize the SendLayer ``Errors`` array from a decoded body.

        SendLayer returns errors as::

            {"Errors": [{"Code": 14, "Message": "..."}]}

        Returns an empty list when absent or malformed.
        """
        raw = data.get("Errors")
        if isinstance(raw, list):
            return [entry for entry in raw if isinstance(entry, dict)]

        return []

    @classmethod
    def _extract_message(cls, data: Dict[str, Any], default: str) -> str:
        """Build a message from the API response, preferring its own text.

        Joins multiple ``Errors`` messages with "; ", then falls back to the
        singular ``Error`` key, then to *default*.
        """
        parts = [
            str(entry["Message"])
            for entry in cls._extract_errors(data)
            if entry.get("Message")
        ]
        if parts:
            return "; ".join(parts)

        error = data.get("Error")
        if isinstance(error, str) and error:
            return error

        return default

    @classmethod
    def _build_error(cls, response: "requests.Response") -> SendLayerError:
        """Map an error response onto the appropriate SendLayer exception."""
        status_code = response.status_code
        data = cls._parse_body(response)
        errors = cls._extract_errors(data)

        exc_class, default = cls._ERROR_MAP.get(status_code, (None, None))
        if exc_class is None:
            default = "Server error" if 500 <= status_code < 600 else "API request failed"
            return SendLayerAPIError(
                message=cls._extract_message(data, default),
                status_code=status_code,
                response=data,
                errors=errors,
            )

        return exc_class(
            cls._extract_message(data, default),
            status_code=status_code,
            response=data,
            errors=errors,
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the SendLayer API.

        Always returns a dict or raises a SendLayerError -- never leaks a
        requests exception to the caller.
        """
        url = f"{self.base_url}/{endpoint}"
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self._session.request(method, url, **kwargs)
        except requests.exceptions.Timeout as exc:
            raise SendLayerError(f"Request timed out after {self.timeout}s") from exc
        except requests.exceptions.RequestException as exc:
            raise SendLayerError(f"Connection error: {exc}") from exc

        if not response.ok:
            raise self._build_error(response)

        # Successful responses with no body (e.g. 204 No Content) decode to {}
        # rather than raising out of response.json().
        if not response.content:
            return {}

        try:
            data = response.json()
        except ValueError as exc:
            raise SendLayerError(
                "Invalid JSON response from API",
                status_code=response.status_code,
            ) from exc

        return data if isinstance(data, (dict, list)) else {}
