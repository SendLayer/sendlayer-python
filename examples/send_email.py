import os
from dotenv import load_dotenv

from sendlayer import (
    SendLayer,
    SendLayerError
)

load_dotenv()

def main():
    # Initialize the email client with your API key
    api_key = os.getenv("SENDLAYER_API_KEY")

    sendlayer = SendLayer(api_key)

    try:
        # Send a simple email
        response = sendlayer.Emails.send(
            to="recipient@example.com",
            from_email="sender@example.com",
            subject="Test Email",
            text="This is a test email sent using the SendLayer Python SDK",
        )
        print(f"Email sent successfully! Message ID: {response['MessageID']}")

        # Send an email with advanced options
        response = sendlayer.Emails.send(
            to=["user1@example.com", "user2@example.co"],
            from_email="sender@example.com",
            subject="Complex Test Email",
            html="<h1>Hello!</h1><p>This is a test email with all options</p>",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            reply_to="reply@example.com",
            attachments=[{
                "path": ".path/to/file.pdf",
                "type": "application/pdf",
            }],
        )
        print(f"Complex email sent successfully! Message ID: {response['MessageID']}")

    
    except SendLayerError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 