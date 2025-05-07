import networkx as nx
from pathlib import Path
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# TASK 6
# The propagation model selected for this task is Independent Cascade (IC)

# Get graph file from data
GRAPH_FILE = Path(__file__).parent / "data" / "communication_updated.graphml"

# Load graph
print(f"Loading Graph from {GRAPH_FILE}")
G = nx.read_graphml(GRAPH_FILE)
print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Save alert_origin node to variable, set up activation_times to track nodes and times and event_queue to keep track of events remaining
start_node = "Node_001"
activation_times = {start_node: 0.0}
event_queue = []

# Initialize event list with attempts from the start node
for neighbor in G.successors(start_node):
    edge_data = G.get_edge_data(start_node, neighbor)
    delay = float(edge_data.get("delay"))

    # Add event to queue
    event_queue.append((0.0 + delay, neighbor, start_node))

processed_events = 0
# Loop while events in queue
while event_queue:
    processed_events += 1
    # Sort event queue by time in each iteration
    event_queue.sort()
    # Get and remove the earliest event from queue
    activation_attempt_time, target_node, source_node = event_queue.pop(0)

    # Check if activation is a success based on reliability
    edge_data = G.get_edge_data(source_node, target_node)
    realiability = float(edge_data.get("reliability"))

    if random.random() <= realiability:
        # Activation successful
        activation_times[target_node] = activation_attempt_time

        # Schedule activation attempts for its neighbors
        for neighbor in G.successors(target_node):
            # Only schedule unactivated neighbors
            if neighbor not in activation_times:
                neighbor_edge_data = G.get_edge_data(target_node, neighbor)
                delay = float(neighbor_edge_data.get("delay"))

                # Time when neighbor will receive the message
                neighbor_activation_time = activation_attempt_time + delay
                # Append new event to event queue
                event_queue.append((neighbor_activation_time, neighbor, target_node))

print(f"\nSimulation finished. Processed {processed_events} potential events.")
print(f"{len(activation_times)} out of {G.number_of_nodes()} nodes activated.")

# Visualize results

plt.figure(figsize=(12, 10))
# Determine simple node colors
node_colors = []
color_map = {"start": "green", "activated": "red", "inactive": "lightgrey"}
for node in G.nodes():
    if node == start_node:
        node_colors.append(color_map["start"])
    elif node in activation_times:
        node_colors.append(color_map["activated"])
    else:
        node_colors.append(color_map["inactive"])

# Draw the graph with simple colors and uniform node size
nx.draw_networkx_edges(
    G, pos=nx.spring_layout(G, seed=42), alpha=0.1, edge_color="gray", width=0.5
)
nx.draw_networkx_nodes(
    G, pos=nx.spring_layout(G, seed=42), node_color=node_colors, node_size=40, alpha=0.9
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
plt.title("Network Graph Highlighting Activated Nodes")
plt.axis("off")
plt.show()

# Analyze results

# Extract times for analysis
times_list = list(activation_times.values())
max_time = np.max(times_list)
avg_time = np.mean(times_list)
reach_fraction = len(activation_times) / G.number_of_nodes()

print(f"Alert Reach: {reach_fraction:.2%}")
print(f"Max Activation Time (Simulation Duration): {max_time:.2f} seconds")
print(f"Average Activation Time (among activated): {avg_time:.2f} seconds")


# TASK 7
# Create pandas dataframe from activation_times
timestamp_records = []
for node, time in activation_times.items():
    timestamp_records.append({"node_id": node, "activation_time": time})

timestamps_df = pd.DataFrame(timestamp_records)

# Add node type information from the graph
node_type_map = nx.get_node_attributes(G, "node_type")
timestamps_df["node_type"] = (
    timestamps_df["node_id"].map(node_type_map).fillna("Unknown")
)

# Calculate delay (GDACS alert origin is 0.0 => no subtraction needed)
timestamps_df["delay"] = timestamps_df["activation_time"]

# Group nodes by type, calculate average, minimum and maximum delays and rename columns
delay_stats_df = (
    timestamps_df.groupby("node_type")["delay"]
    .agg(["mean", "min", "max", "count"])
    .reset_index()
)
delay_stats_df = delay_stats_df.rename(
    columns={
        "mean": "Average delay (s)",
        "min": "Minimum delay (s)",
        "max": "Maximum delay (s)",
        "count": "Nodes activated",
    }
)

print("\nPropagation delay for each group:")
print(delay_stats_df)

# Visualize results
fig, ax = plt.subplots(figsize=(10, 6))

# Create indexes for bar plot
plot_data = delay_stats_df.set_index("node_type")[
    ["Average delay (s)", "Minimum delay (s)", "Maximum delay (s)"]
]

# Create bar plot and add labels
plot_data.plot(kind="bar", ax=ax)
ax.set_xlabel("Stakeholder type", color="red")
ax.set_ylabel("Delay (s)", color="red")
ax.tick_params(axis="x", rotation=0)

# Add title
plt.title(f"Bar Plot Comparing Alert Delays")
plt.show()

# Save results
output_path = Path(__file__).parent / "data" / "timestamps_delay.csv"
timestamps_df.to_csv(output_path, index=False)
