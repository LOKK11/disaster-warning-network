import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# Get graph file from data
GRAPH_FILE = Path(__file__).parent / "data" / "communication_updated.graphml"

# Load graph
print(f"Loading Graph from {GRAPH_FILE}")
G = nx.read_graphml(GRAPH_FILE)
print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Calculate centrality scores
centrality_scores = {}

# Degree centrality
centrality_scores["degree"] = nx.degree_centrality(G)

# Closeness centrality, use delay as distance
centrality_scores["closeness"] = nx.closeness_centrality(G, distance="delay")

# Betweenness centrality, use delay as weight
centrality_scores["betweenness"] = nx.betweenness_centrality(
    G, weight="delay", normalized=True
)

# Eigenvector centrality, use "weight" calculated in task 5 as weight
centrality_scores["eigenvector"] = nx.eigenvector_centrality(
    G, weight="weight", max_iter=500
)

# Combine results into DataFrame

# Create DataFrame with degree centrality
centrality_df = pd.DataFrame.from_dict(
    centrality_scores["degree"], orient="index", columns=["degree"]
)

# Add other centralities with for loop
for name, scores_dict in centrality_scores.items():
    if name != "degree":
        centrality_df[name] = pd.Series(scores_dict)

# Add node type from graph attributes
node_type_map = nx.get_node_attributes(G, "node_type")
centrality_df["node_type"] = centrality_df.index.map(node_type_map)

# Rank nodes
rank_cols = []
for col in centrality_scores.keys():
    if col in centrality_df.columns:
        rank_col = f"{col}_rank"
        centrality_df[rank_col] = centrality_df[col].rank(ascending=False, method="min")
        rank_cols.append(rank_col)

# Identify constantly high-ranked nodes
# Set up parameters for analysis
TOP_N_RANK = 15  # How many top nodes per centrality to consider
MIN_CENTRALITY_COUNT = 3  # Node must be in top 15 for at least in 3 centralities

is_top_n = centrality_df[rank_cols] <= TOP_N_RANK
centrality_df["top_n_count"] = is_top_n.sum(axis=1)

critical_nodes_df = centrality_df[
    centrality_df["top_n_count"] >= MIN_CENTRALITY_COUNT
].sort_values("top_n_count", ascending=False)
critical_nodes_list = critical_nodes_df.index.tolist()

print(
    f"\n{len(critical_nodes_list)} critical nodes found (Top {TOP_N_RANK} in >= {MIN_CENTRALITY_COUNT} measures):"
)
print(critical_nodes_df[["node_type", "top_n_count"] + rank_cols])

# Visualize results
plt.figure(figsize=(15, 12))
pos = nx.spring_layout(G, seed=42)

# Change size and color for critical nodes
node_sizes = []
node_colors = []
for node in G.nodes():
    if node in critical_nodes_list:
        node_sizes.append(150)
        node_colors.append("red")
    else:
        node_sizes.append(50)
        node_colors.append("lightgrey")

nx.draw_networkx_edges(G, pos=pos, alpha=0.1, edge_color="gray", width=0.5)
nx.draw_networkx_nodes(
    G, pos=pos, node_color=node_colors, node_size=node_sizes, alpha=0.9
)

# Get node types for each node
node_type_map = nx.get_node_attributes(G, 'node_type')

# Add labels for critical nodes
labels = {}
for node in critical_nodes_list:
    labels[node] = node_type_map.get(node)

nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=8, font_weight="bold")

# Add title
plt.title("Critical nodes based on Top {TOP_N_RANK} centrality rankings")
plt.axis("off")
plt.show()