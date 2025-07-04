import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sendlayer import (
    SendLayer,
    SendLayerError
)

load_dotenv()

def main():
    # Initialize the events client with your API key
    api_key = os.getenv("SENDLAYER_API_KEY")

    sendlayer = SendLayer(api_key)

    try:
        # Get all events
        print("Retrieving all events...")
        events = sendlayer.Events.get()
        print(events)

        # Get events with filters
        print("\nRetrieving events from the last 2 hours...")
        filtered_events = sendlayer.Events.get(
            start_date=datetime.now() - timedelta(hours=2),
            end_date=datetime.now(),
            event='opened'
            )
        print(filtered_events)

        # Get all events with the 'opened' status
        filtered_by_event = sendlayer.Events.get(event="opened")
        print(filtered_by_event)

    except SendLayerError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 