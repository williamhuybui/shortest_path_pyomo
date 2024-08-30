import dash_cytoscape as cyto

def cytograph(elements):
    return cyto.Cytoscape(
        elements = elements,
        layout={"name": "circle"},
        stylesheet=[
            {"selector": "node", "style": {"label": "data(label)"}},
                        {"selector": ".source-node", "style": {"background-color": "green"}},  # Source node style
                {"selector": ".target-node", "style": {"background-color": "red"}},    # Target node style
                {"selector": ".normal-node", "style": {"background-color": "gray"}},
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "label": "data(label)",
                    "text-rotation": "autorotate",
                    "font-size": "14px",
                    "line-color": "#0074D9",
                    "target-arrow-color": "#0074D9",
                    "text-margin-y": -10,
                },
            },
        ],
        style={'width': '100%', 'height': '500px'},
)

def csv_to_graph_elements(data, source_node=None, target_node=None, shortest_path=[]):
    elements = []
    
    # Get all the nodes
    nodes = set(
        [entry["source"] for entry in data]
        + [entry["target"] for entry in data if entry["target"]]
    )

    # Add nodes with styles if they match source_node or target_node
    for node in nodes:
        if node == source_node:
            elements.append({
                "data": {"id": node, "label": node},
                "classes": "source-node"  # Use a class for source node
            })
        elif node == target_node:
            elements.append({
                "data": {"id": node, "label": node},
                "classes": "target-node"  # Use a class for target node
            })
        else:
            elements.append({"data": {"id": node, "label": node},
                             "classes": "normal-node"},
                            )

    
    # Add edges and highlight the shortest path with pink color
    for entry in data:
        if entry["source"] and entry["target"]:
            # Check if the edge is in the shortest path
            if (entry["source"], entry["target"]) in shortest_path:
                elements.append({
                    "data": {
                        "source": entry["source"],
                        "target": entry["target"],
                        "label": f"{entry['weight']}",
                        "weight": entry["weight"],
                    },
                    "style": {"line-color": "red"},
                })
            else:
                elements.append({
                    "data": {
                        "source": entry["source"],
                        "target": entry["target"],
                        "label": f"{entry['weight']}",
                        "weight": entry["weight"],
                    }
                })
    return elements