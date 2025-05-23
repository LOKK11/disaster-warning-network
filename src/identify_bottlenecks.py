import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Get graph file from data
GRAPH_FILE = Path(__file__).parent / "data" / "communication_updated.graphml"

# Load graph
print(f"Loading Graph from {GRAPH_FILE}")
G = nx.read_graphml(GRAPH_FILE)
print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Load timestamps data
timestamps_list = Path(__file__).parent / "data" / "timestamps_delay.csv"
timestamps_df = pd.read_csv(timestamps_list)

# Exclude alert origin (delay 0.0) from calculations
valid_delays = timestamps_df[timestamps_df["delay"] > 0.0]["delay"]

# Set high delay threshold as 60% and create a set of high delay nodes with that threshold
high_delay_threshold = np.percentile(valid_delays, 60)
high_delay_nodes = set(
    timestamps_df[timestamps_df["delay"] >= high_delay_threshold]["node_id"]
)

print(f"\nDelay threshold: {high_delay_threshold}s")
print(f"{len(high_delay_nodes)} nodes found with high delay")

# Calculate betweenness centrality for each node weighted by delay
betweenness_centrality = nx.betweenness_centrality(G, weight="delay")

# Identify nodes with high betweenness centrality
# Filter out zero centrality values
centrality_values = np.array([c for c in betweenness_centrality.values() if c > 0.0])

# Set high centrality threshold as 60% and create an array of high centrality nodes with that threshold
high_centrality_threshold = np.percentile(centrality_values, 60)
high_centrality_nodes = {
    node
    for node, centrality in betweenness_centrality.items()
    if centrality >= high_centrality_threshold and centrality > 0
}

print(f"\nCentrality threshold: {high_centrality_threshold}")
print(f"{len(high_centrality_nodes)} nodes found with high centrality.")

# Find bottlenecks (nodes with high delay and high centrality)
bottlenecks = list(high_delay_nodes.intersection(high_centrality_nodes))

# Exclude start node (Node_001) from being a bottleneck
bottlenecks = [node for node in bottlenecks if node != "Node_001"]

if bottlenecks:
    print(f"\n{len(bottlenecks)} potential bottleneck nodes found.")
    print(bottlenecks)
else:
    print("No bottleneck nodes found")

# Visualize results
plt.figure(figsize=(15, 12))
pos = nx.spring_layout(G, seed=42)

node_colors = []
node_sizes = []
labels = {}
# Get node types for each node
node_type_map = nx.get_node_attributes(G, 'node_type')

color_map = {"start": "green", "bottleneck": "red", "other": "lightgrey"}
for node in G.nodes():
    if node == "Node_001":
        node_colors.append(color_map["start"])
        node_sizes.append(40)
        labels[node] = node_type_map.get(node) # Add label for start node
    elif node in bottlenecks:
        node_colors.append(color_map["bottleneck"])
        node_sizes.append(140)
        labels[node] = node_type_map.get(node) # Add label if a node is a bottleneck node
    else:
        node_colors.append(color_map["other"])
        node_sizes.append(40)

nx.draw_networkx_edges(
    G, pos=nx.spring_layout(G, seed=42), alpha=0.1, edge_color="gray", width=0.5
)
nx.draw_networkx_nodes(
    G,
    pos=nx.spring_layout(G, seed=42),
    node_color=node_colors,
    node_size=node_sizes,
    alpha=0.9,
)

nx.draw_networkx_labels(
    G, pos=pos, labels=labels, font_size=8, font_weight="bold"
)

# Add legend
legend_handles = [
    plt.Line2D(
        [0], [0], marker="o", color="w", label=t, markersize=8, markerfacecolor=c
    )
    for t, c in color_map.items()
]
legend1 = plt.legend(
    handles=legend_handles,
    title="Node Types",
    loc="upper right",
    bbox_to_anchor=(1.0, 1.0),
)

# Add title
plt.title("Network Graph Highlighting Potential Bottlenecks")
plt.axis("off")
plt.show()