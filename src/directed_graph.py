import pandas as pd
import networkx as nx
from pathlib import Path

nodes_path = Path(__file__).parent / "data" / "nodes.csv"
messages_path = Path(__file__).parent / "data" / "message_records.csv"
nodes_df = pd.read_csv(nodes_path)
messages_df = pd.read_csv(messages_path)

# Construct a directed graph
G = nx.DiGraph()

# Add nodes to the graph
for _, row in nodes_df.iterrows():
    node = row["node_id"]
    G.add_node(node)
    G.nodes[node]["node_type"] = row["node_type"]
    G.nodes[node]["latitude"] = row["latitude"]
    G.nodes[node]["longitude"] = row["longitude"]
    G.nodes[node]["role_priority"] = row["role_priority"]
    G.nodes[node]["capacity"] = row["capacity"]
    G.nodes[node]["influence_score"] = row["influence_score"]

# Assing relevant edge attributes from grouped messages
messages_group = messages_df.groupby(["source_node_id", "destination_node_id"])
for message in messages_group:
    src = message[0][0]
    tgt = message[0][1]
    avg_delay = round(float(message[1]["delay_in_seconds"].mean()), 2)
    avg_reliability = round(float(message[1]["reliability_score"].mean()), 2)
    message_count = int(message[1]["message_type"].count())
    G.add_edge(src, tgt, delay=avg_delay, reliability=avg_reliability, messages=message_count)

# Graph direction and connection validation
print(f"Graph is directed: {nx.is_directed(G)}")
print(f"Graph is connected: {nx.is_weakly_connected(G)}")

# Export the graph
graph_path = Path(__file__).parent / "data" / "communication.graphml"
nx.write_graphml(G, graph_path)
print(f"Graph exported to {graph_path}")
