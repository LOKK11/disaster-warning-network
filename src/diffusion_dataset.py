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

# From message records, get the sent timestamp of a node
def get_timestamp_sent(node_id):
    for message in message_records:
        if message["source_node_id"] == node_id:
            return datetime.fromisoformat(message["timestamp_sent"])
    return alert_time

# Randomly generate connections between all nodes
for i in range(len(PROPAGATION_PATH) - 1):
    source_nodes = nodes_df[nodes_df["node_type"] == PROPAGATION_PATH[i]]
    target_nodes = nodes_df[nodes_df["node_type"] == PROPAGATION_PATH[i + 1]]
    time_sent = alert_time
    for _, target in target_nodes.iterrows():
        random_node = source_nodes.sample(1).iloc[0]
        processing_delay = random.randint(DELAY_MIN, DELAY_MAX / 3)
        time_sent = get_timestamp_sent(random_node["node_id"]) + timedelta(seconds=processing_delay)
        transmission_delay = random.randint(DELAY_MIN, DELAY_MAX)
        time_received = time_sent + timedelta(seconds=transmission_delay)
        message_records.append({
            "source_node_id": random_node["node_id"],
            "destination_node_id": target["node_id"],
            "message_type": random.choice(MESSAGE_TYPES),
            "timestamp_sent": time_sent.isoformat(),
            "timestamp_received": time_received.isoformat(),
            "delay_in_seconds": transmission_delay,
            "reliability_score": round(random.uniform(RELIABILITY_MIN, RELIABILITY_MAX), 2),
        })

# Randomly generate at least 300 message records
while len(message_records) < 300:
    path_nodes = []
    for node_type in PROPAGATION_PATH:
        type_nodes = nodes_df[nodes_df["node_type"] == node_type]
        random_node = type_nodes.sample(1).iloc[0]
        path_nodes.append(random_node)
    time_sent = alert_time
    for i in range(len(path_nodes) - 1):
        transmission_delay = random.randint(DELAY_MIN, DELAY_MAX)
        time_received = time_sent + timedelta(seconds=transmission_delay)
        message_records.append({
            "source_node_id": path_nodes[i]["node_id"],
            "destination_node_id": path_nodes[i + 1]["node_id"],
            "message_type": random.choice(MESSAGE_TYPES),
            "timestamp_sent": time_sent.isoformat(),
            "timestamp_received": time_received.isoformat(),
            "delay_in_seconds": transmission_delay,
            "reliability_score": round(random.uniform(RELIABILITY_MIN, RELIABILITY_MAX), 2),
        })
        # Delay to not send the received message immediately
        processing_delay = random.randint(DELAY_MIN, DELAY_MAX / 3)
        time_sent = time_received + timedelta(seconds=processing_delay)

messages_df = pd.DataFrame(message_records)
output_path = Path(__file__).parent / "data" / "message_records.csv"
messages_df.to_csv(output_path, index=False)

print(f"Synthetic alert diffusion dataset exported to {output_path}")
