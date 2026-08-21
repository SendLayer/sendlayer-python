"""Timeout behaviour.

requests applies no timeout by default and Session.request() ignores any
`timeout` attribute set on the session, so the SDK must pass it per call.
"""
import pytest
import requests

from sendlayer.base.base import BaseClient
from sendlayer.exceptions import SendLayerError


def client_recording_kwargs(monkeypatch, config=None):
    client = BaseClient("test-api-key", config)
    seen = {}

    def _record(method, url, **kwargs):
        seen.clear()
        seen.update(kwargs)
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"ok": true}'
        return response

    monkeypatch.setattr(client._session, "request", _record)
    return client, seen


def test_default_timeout_is_applied(monkeypatch):
    client, seen = client_recording_kwargs(monkeypatch)
    client._make_request("GET", "webhooks")
    assert seen["timeout"] == BaseClient.DEFAULT_TIMEOUT


def test_timeout_is_configurable_at_top_level(monkeypatch):
    client, seen = client_recording_kwargs(monkeypatch, {"timeout": 5})
    client._make_request("GET", "webhooks")
    assert seen["timeout"] == 5


def test_timeout_is_configurable_under_requests_key(monkeypatch):
    """The documented `requests: {timeout: N}` form used to be a silent no-op."""
    client, seen = client_recording_kwargs(monkeypatch, {"requests": {"timeout": 7}})
    client._make_request("GET", "webhooks")
    assert seen["timeout"] == 7


def test_explicit_per_call_timeout_wins(monkeypatch):
    client, seen = client_recording_kwargs(monkeypatch, {"timeout": 5})
    client._make_request("GET", "webhooks", timeout=1)
    assert seen["timeout"] == 1


def test_session_timeout_attribute_is_not_honoured_by_requests():
    """Documents why this fix is needed at all."""
    import inspect
    source = inspect.getsource(requests.sessions.Session.request)
    assert "self.timeout" not in source


def test_timeout_raises_sendlayer_error(monkeypatch):
    client = BaseClient("test-api-key", {"timeout": 3})

    def _raise(*args, **kwargs):
        raise requests.exceptions.ConnectTimeout("timed out")

    monkeypatch.setattr(client._session, "request", _raise)

    with pytest.raises(SendLayerError, match="Request timed out after 3s"):
        client._make_request("GET", "webhooks")


def test_connection_error_raises_sendlayer_error(monkeypatch):
    client = BaseClient("test-api-key")

    def _raise(*args, **kwargs):
        raise requests.exceptions.ConnectionError("name resolution failed")

    monkeypatch.setattr(client._session, "request", _raise)

    with pytest.raises(SendLayerError, match="Connection error"):
        client._make_request("GET", "webhooks")
