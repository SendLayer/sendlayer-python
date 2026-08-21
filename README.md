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
from sendlayer import SendLayer

# Initialize the email client with your API key
sendlayer = SendLayer("your-api-key")

# Send an email
response = sendlayer.Emails.send(
    sender="sender@example.com",
    to="recipient@example.com",
    subject="Test Email",
    text="This is a test email"
)
```

## Configuration

Pass an optional config dict when initializing the SDK:

```python
sendlayer = SendLayer("your-api-key", {
    "timeout": 30,                  # HTTP timeout in seconds (default: 30)
    "attachmentURLTimeout": 30000,  # Remote attachment fetch timeout, milliseconds
    "requests": {                   # Extra options for the underlying session
        "headers": {"X-Custom": "value"},
    },
})
```

Requests time out after 30 seconds by default and raise `SendLayerError`. Set
`timeout` to change it, or pass `timeout` to an individual call to override it
for that request.

## Features

- **Email Module**: Send emails with support for HTML/text content, attachments, CC/BCC, and templates
- **Webhooks Module**: Create, retrieve, and delete webhooks for various email events
- **Events Module**: Retrieve email events with filtering options
- **Error Handling**: Typed exceptions carrying the API's own error messages and numeric codes
- **Type Hints**: Full type support for better IDE integration

## Documentation

### Email Module

Send emails using the `SendLayer` module:

```python
from sendlayer import SendLayer

sendlayer = SendLayer(api_key='your-api-key')

# Send an HTML email with a plain-text fallback. Supply both `html` and `text`
# and both parts are sent -- recommended for deliverability. `ContentType` is
# reported to the API as HTML whenever an HTML body is present, and as Text
# when only `text` is supplied.
response = sendlayer.Emails.send(
    sender='sender@example.com',
    to='recipient@example.com',
    subject='Welcome!',
    text='Welcome to our platform!',
    html='<h1>Welcome!</h1><p>Welcome to our platform!</p>'
)


# Send a complex email
response = sendlayer.Emails.send(
    sender={"email": "sender@example.com", "name": "Paulie Paloma"},
    to=[
        {'email': 'recipient1@example.com', 'name': 'Recipient 1'},
        {'email': 'recipient2@example.com', 'name': 'Recipient 2'}
    ],
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
from sendlayer import SendLayer

sendlayer = SendLayer(api_key='your-api-key')

# Create a webhook
# Webhook event options: bounce, click, open, unsubscribe, complaint, delivery

webhook = sendlayer.Webhooks.create(
    url='https://your-domain.com/webhook',
    event='open'
)

# Get all webhooks
webhooks = sendlayer.Webhooks.get()

# Delete a webhook
sendlayer.Webhooks.delete(webhook_id=123)
```

### Events Module

```python
from sendlayer import SendLayer
from datetime import datetime, timedelta

sendlayer = SendLayer(api_key='your-api-key')

# Get all events
events = sendlayer.Events.get()

# Get filtered events
events = sendlayer.Events.get(
    start_date=datetime.now() - timedelta(hours=4),
    end_date=datetime.now(),
    event='opened'
)
```

## Error Handling

Every SDK exception derives from `SendLayerError`, so a single `except` clause
catches them all. Catch a specific subclass first when you need to branch:

```python
from sendlayer import (
    SendLayerError,
    SendLayerRateLimitError,
    SendLayerValidationError,
)

try:
    response = sendlayer.Emails.send(...)
except SendLayerRateLimitError as e:
    print(f"Rate limited: {e.message}")
except SendLayerValidationError as e:
    print(f"Invalid request: {e.message}")
except SendLayerError as e:
    print(f"SendLayer error: {e.status_code} - {e.message}")
```

### Exception Types

- `SendLayerError`: base exception for all SendLayer errors
- `SendLayerAuthenticationError`: invalid API key (401)
- `SendLayerValidationError`: invalid parameters, raised for 400 and 422 as well
  as for input the SDK rejects locally
- `SendLayerNotFoundError`: resource not found (404)
- `SendLayerRateLimitError`: rate limit exceeded (429)
- `SendLayerInternalServerError`: internal server error (500 only)
- `SendLayerAPIError`: any status not covered above, including other 5xx

### Error Details

Every exception carries the same attributes, so you can read them without first
checking which subclass you caught:

| Attribute | Description |
| --- | --- |
| `message` | The API's own message text, or the SDK's message for local errors |
| `status_code` | HTTP status of the response; `None` for local errors |
| `response` | Decoded response body, or `{}` when unavailable |
| `errors` | Raw SendLayer `Errors` entries, each with a numeric `Code` and `Message` |
| `codes` | The numeric codes from `errors`, for convenient branching |

```python
try:
    response = sendlayer.Emails.send(...)
except SendLayerError as e:
    print(e.message)        # e.g. "Recipient email is suppressed"

    for error in e.errors:
        print(error["Code"], error["Message"])   # e.g. 14 Recipient email is suppressed

    if 14 in e.codes:
        ...  # recipient suppressed
```

`errors` is an empty list when the SDK raises the error locally (input
validation, connection failures) and when the API returns a body that isn't the
JSON `Errors` shape, so guard with `if e.errors:` before relying on it. When the
body isn't JSON at all, `message` falls back to the HTTP reason phrase, e.g.
`"Bad Request"`.

`message` holds the API's text verbatim, joining multiple messages with `; `.
Note that `str(e)` equals `message` for every type except `SendLayerAPIError`,
whose string form keeps an `API Error <status>: ` prefix.

The numeric `Code` values are a fixed set defined by the API — see the
[SendLayer error codes reference](https://developers.sendlayer.com/api-reference/error-codes)
for the full table (`14` = recipient suppressed, `17` = email quota reached,
`32` = domain not activated, and so on).

## More Details
To learn more about using the SendLayer SDK, be sure to check our [Developer Documentation](https://developers.sendlayer.com/sdks/python).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.


## License

MIT License - see [LICENSE](./LICENSE) file for details 