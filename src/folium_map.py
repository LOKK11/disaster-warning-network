import pandas as pd
import networkx as nx
import numpy as np
import folium
from pathlib import Path

# Load node dataset into pandas dataframe
nodes_path = Path(__file__).parent / "data" / "nodes.csv"
nodes_df = pd.read_csv(nodes_path)

# Load graph
graph_path = Path(__file__).parent / "data" / "communication_updated.graphml"
G = nx.read_graphml(graph_path)

# Ensure that latitude and longitude fields are correctly formatted
nodes_df["latitude"] = nodes_df["latitude"].astype(float)
nodes_df["longitude"] = nodes_df["longitude"].astype(float)

# Centrality values
betweenness_centrality = nx.betweenness_centrality(G, weight="delay")
centrality_values = np.array([c for c in betweenness_centrality.values()])

# Normalize centrality values
min_centrality, max_centrality = min(centrality_values), max(centrality_values)
centralities_normalized = np.array(
    [
        round((c - min_centrality) / (max_centrality - min_centrality), 2)
        for c in centrality_values
    ]
)

# Create a folium map located at the average latitude and longitude of the nodes
m = folium.Map(location=[nodes_df["latitude"].mean(), nodes_df["longitude"].mean()])

# Customized colors based on node type
customized_colors = {
    "alert_origin": "red",
    "control_center": "orange",
    "media_outlet": "blue",
    "community_leader": "green",
    "citizen": "gray",
}

# Add circle markers for each node sized by centrality value and colored by node type
for i, row in nodes_df.iterrows():
    node_id = row["node_id"]
    node_type = row["node_type"]
    centrality = centralities_normalized[i]
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=5 + (centrality * 20),
        color=customized_colors.get(node_type),
        fill=True,
        fill_color=customized_colors.get(node_type),
        fill_opacity=0.7,
        popup=f"ID:{node_id} Type:{node_type} Centrality:{centrality}",
    ).add_to(m)

output_path = Path(__file__).parent / "data" / "interactive_map.html"
m.save(output_path)
print(f"Map exported to {output_path}")
