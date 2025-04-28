import pandas as pd
import networkx as nx
from pathlib import Path

nodes_path = Path(__file__).parent / "data" / "nodes.csv"
messages_path = Path(__file__).parent / "data" / "message_records.csv"
nodes_df = pd.read_csv(nodes_path)
messages_df = pd.read_csv(messages_path)

G = nx.DiGraph()

for _, row in nodes_df.iterrows():
    node = row["node_id"]
    G.add_node(node)
    G.nodes[node]["node_type"] = row["node_type"]
    G.nodes[node]["latitude"] = row["latitude"]
    G.nodes[node]["longitude"] = row["longitude"]
    G.nodes[node]["role_priority"] = row["role_priority"]
    G.nodes[node]["capacity"] = row["capacity"]
    G.nodes[node]["influence_score"] = row["influence_score"]

for _, row in messages_df.iterrows():
    source = row["source_node_id"]
    target = row["destination_node_id"]
    G.add_edge(source, target)
    G[source][target]["message_type"] = row["message_type"]
    G[source][target]["timestamp_sent"] = row["timestamp_sent"]
    G[source][target]["timestamp_received"] = row["timestamp_received"]
    G[source][target]["delay"] = row["delay_in_seconds"]
    G[source][target]["reliability"] = row["reliability_score"]

print(f"Graph is directed: {nx.is_directed(G)}")
print(f"Graph is connected: {nx.is_weakly_connected(G)}")
