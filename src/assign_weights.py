import networkx as nx
from pathlib import Path

graph_path = Path(__file__).parent / "data" / "communication.graphml"
output_path = Path(__file__).parent / "data" / "communication_updated.graphml"

G = nx.read_graphml(graph_path)

delay_values = list(nx.get_edge_attributes(G, "delay").values())
reliability_values = list(nx.get_edge_attributes(G, "reliability").values())

delay_min, delay_max = min(delay_values), max(delay_values)
reliability_min, reliability_max = min(reliability_values), max(reliability_values)

# Calculate and assign weights and normalized values to edges
for edge in G.edges(data=True):
    src = edge[0]
    tgt = edge[1]
    delay = edge[2]["delay"]
    reliability = edge[2]["reliability"]
    weight = round(delay / (reliability + 1e-6), 2)  # Avoid division by zero
    delay_normalized = round((delay - delay_min) / (delay_max - delay_min), 2)
    reliability_normalized = round(
        (reliability - reliability_min) / (reliability_max - reliability_min), 2
    )
    G.edges[src, tgt]["weight"] = weight
    G.edges[src, tgt]["delay_normalized"] = delay_normalized
    G.edges[src, tgt]["reliability_normalized"] = reliability_normalized

nx.write_graphml(G, output_path)

print("Calculated values stored as edge attributes.")
