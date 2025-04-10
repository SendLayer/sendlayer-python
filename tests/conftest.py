import pytest
import os
from unittest.mock import Mock, patch
from sendlayer import NewEmail, Webhooks, Events

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = Mock()
    mock.ok = True
    mock.status_code = 200
    return mock

@pytest.fixture
def mock_session(mock_response):
    """Create a mock session object."""
    mock = Mock()
    mock.request.return_value = mock_response
    return mock

@pytest.fixture
def email_client(mock_session):
    """Create a test email client with mocked session."""
    with patch("requests.Session", return_value=mock_session):
        client = NewEmail("test-api-key")
        mock_session.request.return_value.json.return_value = {"MessageID": "test-message-id"}
        
        # Create a test attachment file for tests
        with open("test_attachment.txt", "w") as f:
            f.write("Test content")
            
        yield client
        
        # Clean up the test file after tests
        if os.path.exists("test_attachment.txt"):
            os.remove("test_attachment.txt")

@pytest.fixture
def webhooks_client(mock_session):
    """Create a test webhooks client with mocked session."""
    with patch("requests.Session", return_value=mock_session):
        client = Webhooks("test-api-key")
        # For different methods, we'll return different responses
        # The default for all operations is NewWebhookID
        mock_session.request.return_value.json.return_value = {
            "NewWebhookID": 123,
            "Webhooks": [
                {
                    "WebhookID": 123,
                    "URL": "https://example.com/webhook",
                    "Event": "open"
                }
            ]
        }
        return client

@pytest.fixture
def events_client(mock_session):
    """Create a test events client with mocked session."""
    with patch("requests.Session", return_value=mock_session):
        client = Events("test-api-key")
        # Return the format that matches the events module implementation
        mock_session.request.return_value.json.return_value = {
            "TotalRecords": 2,
            "Events": [
                {
                    "EventType": "opened",
                    "MessageID": "test-message-id",
                    "LoggedTime": 1234567890
                },
                {
                    "EventType": "clicked",
                    "MessageID": "test-message-id-2",
                    "LoggedTime": 1234567891
                }
            ]
        }
        return client 