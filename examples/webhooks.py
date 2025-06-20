import os
from dotenv import load_dotenv
from sendlayer import (
    SendLayer,
    SendLayerError
)

load_dotenv()

def main():
    # Initialize the webhooks client with your API key
    api_key = os.getenv("SENDLAYER_API_KEY")

    sendlayer = SendLayer(api_key)

    try:
        # Create a new webhook
        print("Creating a new webhook...")
        webhook = sendlayer.Webhooks.create(
            url="https://example.com/webhook",
            event="open"
        )
        
        print(f"Webhook created successfully! Details: {webhook}")

        # Get all webhooks
        print("\nRetrieving all webhooks...")
        webhooks = sendlayer.Webhooks.get()
        print(webhooks)

        webhook_id = 987

        # Delete the webhook we created
        print(f"\nDeleting webhook {webhook_id}...")
        sendlayer.Webhooks.delete(webhook_id)
        print("Webhook deleted successfully!")


    except SendLayerError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 