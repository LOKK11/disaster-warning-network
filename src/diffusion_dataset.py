import pandas as pd
import random
from pathlib import Path
from datetime import datetime, timedelta

node_list = Path(__file__).parent / "data" / "nodes.csv"
nodes_df = pd.read_csv(node_list)

PROPAGATION_PATH = [
    "alert_origin",
    "control_center",
    "media_outlet",
    "community_leader",
    "citizen",
]

MESSAGE_TYPES = ["SMS", "App Notification"]
DELAY_MIN, DELAY_MAX = 10, 180  # Seconds
RELIABILITY_MIN, RELIABILITY_MAX = 0, 1

message_records = []
alert_time = datetime.now()

# Generate at least 250 message records
while len(message_records) < 250:
    path_nodes = []
    for node_type in PROPAGATION_PATH:
        type_nodes = nodes_df[nodes_df["node_type"] == node_type]
        random_node = type_nodes.sample(1).iloc[0]
        path_nodes.append(random_node)
    time_sent = alert_time
    for i in range(len(path_nodes) - 1):
        delay = random.randint(DELAY_MIN, DELAY_MAX)
        time_received = time_sent + timedelta(seconds=delay)
        message_records.append({
            "source_node_id": path_nodes[i]["node_id"],
            "destination_node_id": path_nodes[i + 1]["node_id"],
            "message_type": random.choice(MESSAGE_TYPES),
            "timestamp_sent": time_sent.isoformat(),
            "timestamp_received": time_received.isoformat(),
            "delay_in_seconds": delay,
            "reliability_score": round(random.uniform(RELIABILITY_MIN, RELIABILITY_MAX), 2),
        })
        # Delay to not send the received message immediately
        processing_delay = random.randint(DELAY_MIN, 60)
        time_sent = time_received + timedelta(seconds=processing_delay)

messages_df = pd.DataFrame(message_records)
output_path = Path(__file__).parent / "data" / "message_records.csv"
messages_df.to_csv(output_path, index=False)

print(f"Synthetic alert diffusion dataset exported to {output_path}")
