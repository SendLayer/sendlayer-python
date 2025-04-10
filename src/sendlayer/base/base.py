import requests
from typing import Dict, Any
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
    
    def __init__(self, api_key: str):
        """Initialize the base client with API key."""
        self.api_key = api_key
        self.base_url = "https://console.sendlayer.com/api/v1"
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the SendLayer API."""
        url = f"{self.base_url}/{endpoint}"
        response = self._session.request(method, url, **kwargs)
        
        if not response.ok:
            if response.status_code == 401:
                raise SendLayerAuthenticationError("401: Invalid API key")
            elif response.status_code == 400:
                raise SendLayerValidationError(response.json().get("Error", "400: Invalid request parameters"))
            elif response.status_code == 404:
                raise SendLayerNotFoundError(response.json().get("Error", "404: Resource not found"))
            elif response.status_code == 429:
                raise SendLayerRateLimitError(response.json().get("Error", "429: Rate limit exceeded"))
            elif response.status_code == 500:
                raise SendLayerInternalServerError(response.json().get("Error", "500: Internal server error"))
            elif response.status_code == 422:
                raise SendLayerValidationError(response.json().get("Error", "422: Invalid request parameters"))
            else:
                try:
                    response_data = response.json()
                except:
                    response_data = {"error": response.text}
                raise SendLayerAPIError(
                    message=response_data.get("Error", "API error"),
                    status_code=response.status_code,
                    response=response_data
                )
        
        return response.json() 