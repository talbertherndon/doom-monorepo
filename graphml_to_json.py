import networkx as nx
import json

# Load GraphML
graph = nx.read_graphml("ragtest/output/graph.graphml")

# Convert to JSON format with metadata
graph_data = {
    "nodes": [],
    "links": []
}

# Extract nodes with metadata
for node, attrs in graph.nodes(data=True):
    graph_data["nodes"].append({
        "id": node,
        "group": 1,  # Modify group logic if needed
        "metadata": attrs  # Include metadata from GraphML
    })

# Extract edges with metadata
for u, v, attrs in graph.edges(data=True):
    graph_data["links"].append({
        "source": u,
        "target": v,
        "metadata": attrs  # Include edge metadata
    })

# Save JSON
with open("doom-or-boom/src/graph_data.json", "w", encoding="utf-8") as f:
    json.dump(graph_data, f, indent=2, ensure_ascii=False)

print("✅ GraphML converted to JSON with metadata!")