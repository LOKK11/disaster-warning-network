import pandas as pd
from pathlib import Path
import random

# Define the bounding box for Europe (approximate lat/lon ranges)
LAT_MIN, LAT_MAX = 35.0, 70.0
LON_MIN, LON_MAX = -10.0, 40.0

# Define node types and their properties
node_types = [
    {
        "type": "alert_origin",
        "count": 1,
        "role_priority": 5,
        "capacity": 1000,
        "influence_score": 1.0,
    },
    {
        "type": "control_center",
        "count": 10,
        "role_priority": 4,
        "capacity": 500,
        "influence_score": 0.8,
    },
    {
        "type": "media_outlet",
        "count": 20,
        "role_priority": 3,
        "capacity": 200,
        "influence_score": 0.6,
    },
    {
        "type": "community_leader",
        "count": 50,
        "role_priority": 2,
        "capacity": 100,
        "influence_score": 0.4,
    },
    {
        "type": "citizen",
        "count": 100,
        "role_priority": 1,
        "capacity": 10,
        "influence_score": 0.2,
    },
]

# Generate nodes with unique IDs and attributes
nodes = []
node_id = 1
for node_type in node_types:
    for _ in range(node_type["count"]):
        node = {
            "node_id": f"Node_{node_id:03d}",
            "node_type": node_type["type"],
            "latitude": round(random.uniform(LAT_MIN, LAT_MAX), 6),
            "longitude": round(random.uniform(LON_MIN, LON_MAX), 6),
            "role_priority": node_type["role_priority"],
            "capacity": node_type["capacity"],
            "influence_score": node_type["influence_score"],
        }
        nodes.append(node)
        node_id += 1

# Create a DataFrame and export to CSV
nodes_df = pd.DataFrame(nodes)
output_path = Path(__file__).parent / "data" / "nodes.csv"
nodes_df.to_csv(output_path, index=False)

print(f"Nodes data exported to {output_path}")
