import os
from dotenv import load_dotenv
from sendlayer import (
    Webhooks,
    SendLayerError
)

load_dotenv()

def main():
    # Initialize the webhooks client with your API key
    api_key = os.getenv("SENDLAYER_API_KEY")

    client = Webhooks(api_key)

    try:
        # Create a new webhook
        print("Creating a new webhook...")
        webhook = client.create(
            url="https://example.com/webhook",
            event="opened"
        )
        
        print(f"Webhook created successfully! Details: {webhook}")

        # Get all webhooks
        print("\nRetrieving all webhooks...")
        webhooks = client.get_all()
        print(webhooks)

        webhook_id = 987

        # Delete the webhook we created
        print(f"\nDeleting webhook {webhook_id}...")
        client.delete(webhook_id)
        print("Webhook deleted successfully!")


    except SendLayerError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 