import json
from gdacs.api import GDACSAPIReader
from datetime import datetime, timedelta, timezone
import pandas as pd
from pathlib import Path

client = GDACSAPIReader()
# Define the date range: past two years
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(days=730)
# Fetch latest flood events
events = client.latest_events(event_type="FL")
# Access the 'features' list within the GeoJSON response
events_features = events.features

print(f"Number of events {len(events_features)}")

# Make pandas DataFrame from the countries csv
countries_df = pd.read_csv(
    f"{Path(__file__).parent}/data/Countries-Europe.csv", usecols=["name"]
)

# Filter events to only include those in Europe
filtered_events = [
    event
    for event in events_features
    if event["properties"]["country"] in countries_df["name"].values
]

print(f"Number of events in Europe {len(filtered_events)}")

# Filter events to 2 last years
filtered_events = [
    event
    for event in filtered_events
    if start_date
    <= datetime.fromisoformat(filtered_events[0]["properties"]["fromdate"]).replace(
        tzinfo=timezone.utc
    )
    <= end_date
]

print(f"Number of events in Europe in the last 2 years {len(filtered_events)}")

print(f"Filtered events: {json.dumps(filtered_events, indent=2)}")


# Export to CSV
def export_to_csv(events, filename):
    # Create a DataFrame from the events
    df = pd.DataFrame(events)
    # Save to CSV
    df.to_csv(filename, index=False)


export_to_csv(
    filtered_events,
    f"{Path(__file__).parent}/data/flood_events.csv",
)
