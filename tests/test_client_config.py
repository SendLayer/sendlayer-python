"""The public SendLayer entry point must forward config and export exceptions."""
import sendlayer
from sendlayer import SendLayer
from sendlayer.base.base import BaseClient


def test_config_is_forwarded_to_the_client():
    client = SendLayer("test-api-key", {"timeout": 5})
    assert client.Emails.client.timeout == 5


def test_default_timeout_when_no_config():
    client = SendLayer("test-api-key")
    assert client.Emails.client.timeout == BaseClient.DEFAULT_TIMEOUT


def test_attachment_timeout_is_forwarded():
    client = SendLayer("test-api-key", {"attachmentURLTimeout": 1234})
    assert client.Emails.client.attachment_url_timeout == 1234


def test_modules_share_one_client():
    client = SendLayer("test-api-key", {"timeout": 9})
    assert client.Emails.client is client.Webhooks.client
    assert client.Emails.client is client.Events.client


def test_all_exception_types_are_importable_from_the_package():
    for name in [
        "SendLayerError",
        "SendLayerAPIError",
        "SendLayerAuthenticationError",
        "SendLayerNotFoundError",
        "SendLayerRateLimitError",
        "SendLayerValidationError",
        "SendLayerInternalServerError",
    ]:
        assert hasattr(sendlayer, name), f"{name} is not exported"
        assert name in sendlayer.__all__
