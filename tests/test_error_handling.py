"""Error-path tests.

These build real ``requests.Response`` objects rather than Mocks, because a
Mock's ``.json()`` never raises -- which is exactly the failure mode these
tests exist to cover.
"""
import json

import pytest
import requests

from sendlayer.base.base import BaseClient
from sendlayer.exceptions import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerValidationError,
    SendLayerNotFoundError,
    SendLayerRateLimitError,
    SendLayerInternalServerError,
)

REASONS = {
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    204: "No Content",
}


def make_response(status, body="", content_type="application/json"):
    response = requests.Response()
    response.status_code = status
    response._content = body.encode() if isinstance(body, str) else body
    response.headers["Content-Type"] = content_type
    response.reason = REASONS.get(status, "")
    return response


def call(monkeypatch, response):
    client = BaseClient("test-api-key")
    monkeypatch.setattr(client._session, "request", lambda *a, **kw: response)
    return client._make_request("POST", "email")


def api_error_body(*pairs):
    return json.dumps({"Errors": [{"Code": c, "Message": m} for c, m in pairs]})


@pytest.mark.parametrize(
    "status,exc_class",
    [
        (400, SendLayerValidationError),
        (401, SendLayerAuthenticationError),
        (404, SendLayerNotFoundError),
        (422, SendLayerValidationError),
        (429, SendLayerRateLimitError),
        (500, SendLayerInternalServerError),
    ],
)
def test_status_maps_to_exception_and_surfaces_api_message(monkeypatch, status, exc_class):
    body = api_error_body((14, "Recipient email is suppressed"))

    with pytest.raises(exc_class) as info:
        call(monkeypatch, make_response(status, body))

    err = info.value
    # The API's own message, not a hardcoded default.
    assert err.message == "Recipient email is suppressed"
    assert err.status_code == status
    assert err.errors == [{"Code": 14, "Message": "Recipient email is suppressed"}]
    assert err.codes == [14]


def test_multiple_error_messages_are_joined(monkeypatch):
    body = api_error_body((2, "Missing FromName"), (8, "Missing Subject"))

    with pytest.raises(SendLayerValidationError) as info:
        call(monkeypatch, make_response(400, body))

    assert info.value.message == "Missing FromName; Missing Subject"
    assert info.value.codes == [2, 8]


def test_unmapped_status_raises_api_error(monkeypatch):
    body = api_error_body((14, "Recipient email is suppressed"))

    with pytest.raises(SendLayerAPIError) as info:
        call(monkeypatch, make_response(502, body))

    err = info.value
    assert err.status_code == 502
    assert err.message == "Recipient email is suppressed"
    # Historical string form keeps the status prefix.
    assert str(err) == "API Error 502: Recipient email is suppressed"


def test_non_json_error_body_falls_back_to_reason_phrase(monkeypatch):
    """A proxy returning HTML must still raise a SendLayerError, not JSONDecodeError."""
    with pytest.raises(SendLayerValidationError) as info:
        call(monkeypatch, make_response(400, "<html>Bad Request</html>", "text/html"))

    assert info.value.message == "Bad Request"
    assert info.value.errors == []


def test_json_decode_error_is_never_leaked(monkeypatch):
    """Guards the contract: no requests exception escapes _make_request."""
    with pytest.raises(SendLayerError):
        call(monkeypatch, make_response(400, "not json at all", "text/html"))


def test_legacy_singular_error_key_is_used(monkeypatch):
    body = json.dumps({"Error": "legacy shape"})

    with pytest.raises(SendLayerValidationError) as info:
        call(monkeypatch, make_response(400, body))

    assert info.value.message == "legacy shape"


def test_malformed_errors_array_is_ignored(monkeypatch):
    body = json.dumps({"Errors": "not-a-list"})

    with pytest.raises(SendLayerValidationError) as info:
        call(monkeypatch, make_response(400, body))

    assert info.value.errors == []
    assert info.value.message == "Invalid request parameters"


def test_empty_success_body_returns_empty_dict(monkeypatch):
    """204 No Content must not raise out of response.json()."""
    assert call(monkeypatch, make_response(204, b"")) == {}


def test_invalid_json_on_success_raises_sendlayer_error(monkeypatch):
    with pytest.raises(SendLayerError, match="Invalid JSON response"):
        call(monkeypatch, make_response(200, "not json", "text/html"))


def test_successful_response_is_returned(monkeypatch):
    body = json.dumps({"MessageID": "abc"})
    assert call(monkeypatch, make_response(200, body)) == {"MessageID": "abc"}


def test_errors_attribute_exists_on_locally_raised_exceptions():
    """Every exception type exposes the same attributes, not just APIError."""
    err = SendLayerValidationError("local failure")
    assert err.errors == []
    assert err.codes == []
    assert err.status_code is None
    assert err.response == {}
    assert err.message == "local failure"
    assert str(err) == "local failure"
