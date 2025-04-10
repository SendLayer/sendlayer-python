<a href="https://sendlayer.com">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-dark.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-light.svg">
  <img alt="SendLayer Logo" width="200px" src="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-light.svg">
</picture>
</a>

### SendLayer Python SDK

The official Python SDK for interacting with the SendLayer API, providing a simple and intuitive interface for sending emails, managing webhooks, and retrieving email events.

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)


## Installation

```bash
pip install sendlayer
```

## Quick Start

```python
from sendlayer import NewEmail

# Initialize the email client with your API key
sendlayer = NewEmail("your-api-key")

# Send an email
response = sendlayer.send(
    to="recipient@example.com",
    from_email="sender@example.com",
    subject="Test Email",
    text="This is a test email"
)
```

## Features

- **Email Module**: Send emails with support for HTML/text content, attachments, CC/BCC, and templates
- **Webhooks Module**: Create, retrieve, and delete webhooks for various email events
- **Events Module**: Retrieve email events with filtering options
- **Error Handling**: Custom exceptions for better error management
- **Type Hints**: Full type support for better IDE integration

## Documentation

### Email Module

Send emails using the `NewEmail` module:

```python
from sendlayer import NewEmail

sendlayer = NewEmail(api_key='your-api-key')


# Send a complex email
response = sendlayer.send(
    to=[
        {'email': 'recipient1@example.com', 'name': 'Recipient 1'},
        {'email': 'recipient2@example.com', 'name': 'Recipient 2'}
    ],
    from_email='sender@example.com',
    from_name='Sender Name',
    subject='Complex Email',
    html='<p>This is a <strong>test email</strong>!</p>',
    text='This is a test email!',
    cc=[{'email': 'cc@example.com', 'name': 'CC Recipient'}],
    bcc=[{'email': 'bcc@example.com', 'name': 'BCC Recipient'}],
    reply_to=[{'email': 'reply@example.com', 'name': 'Reply To'}],
    attachments=[{
        'path': 'path/to/file.pdf',
        'type': 'application/pdf',
    }]
)
```

### Webhooks Module

```python
from sendlayer import Webhooks

sendlayer = Webhooks(api_key='your-api-key')

# Create a webhook
# Webhook event options: bounce, click, open, unsubscribe, complaint, delivery

webhook = sendlayer.create(
    url='https://your-domain.com/webhook',
    event='open'
)

# Get all webhooks
webhooks = sendlayer.get_all()

# Delete a webhook
sendlayer.delete(webhook_id=123)
```

### Events Module

```python
from sendlayer import Events
from datetime import datetime, timedelta

sendlayer = Events(api_key='your-api-key')

# Get all events
events = sendlayer.get()

# Get filtered events
events = sendlayer.get(
    start_date=datetime.now() - timedelta(hours=4),
    end_date=datetime.now(),
)
```

## Error Handling

The SDK provides custom exceptions for better error handling:

```python
from sendlayer import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerValidationError
)

try:
    response = sendlayer.send(...)
except SendLayerAuthenticationError:
    print("Invalid API key")
except SendLayerValidationError:
    print("Invalid request parameters")
except SendLayerError as e:
    print(f"API error: {e.status_code} - {e.message}")
except SendLayerError:
    print("An unexpected error occurred")
```

## Development

### Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

## License

MIT License - see [LICENSE](./LICENSE) file for details 