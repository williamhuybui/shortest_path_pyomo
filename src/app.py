import dash
from dash import dcc, html, Input, Output, State
import networkx as nx
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dash_table
from cyto_components import cytograph, csv_to_graph_elements
from solver import find_shortest_path_glpk

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

example_1_df = pd.read_csv("src/data/example_2_dg.csv")
example_2_df = pd.read_csv("src/data/example_1_dg.csv")
example_3_df = pd.read_csv("src/data/example_3_dg.csv")

app.layout = dbc.Container(
    [
        dbc.Container(
            [
                html.H1(
                    "Shortest Path Using Optimization Solver",
                    className="display-4 text-center",
                ),
            ],
            fluid=True,
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Input(
                                    id="node-input",
                                    type="text",
                                    placeholder="Enter node name",
                                ),
                                html.Button(
                                    "Add Node", id="add-node-button", n_clicks=0
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="node-list-remove",
                                    multi=True,
                                    placeholder="Select nodes to remove",
                                    style={"width": "300px"},
                                ),
                                html.Button(
                                    "Remove Node", id="remove-node-button", n_clicks=0
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                    ],
                    style={"margin-bottom": "20px"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="source-node-input",
                                    placeholder="Source node",
                                    style={"width": "150px"},
                                ),
                                dcc.Dropdown(
                                    id="target-node-input",
                                    placeholder="Target node",
                                    style={"width": "150px"},
                                ),
                                dcc.Input(
                                    id="weight-input",
                                    type="number",
                                    placeholder="Edge weight",
                                    min=1,
                                    style={"width": "150px"},
                                ),
                                html.Button(
                                    "Add Edge", id="add-edge-button", n_clicks=0
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="edge-list-remove",
                                    multi=True,
                                    placeholder="Select edges to remove",
                                    style={"width": "300px"},
                                ),
                                html.Button(
                                    "Remove Edge", id="remove-edge-button", n_clicks=0
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                    ],
                    style={"margin-bottom": "20px"},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Example 1",
                                    color="primary",
                                    id="example_1-btn",
                                    style={"margin-right": "10px"},
                                ),
                                dbc.Button(
                                    "Example 2",
                                    color="primary",
                                    id="example_2-btn",
                                    style={"margin-right": "10px"},
                                ),
                                dbc.Button(
                                    "Texas Big Cities",
                                    color="primary",
                                    id="example_3-btn",
                                    style={"margin-right": "10px"},
                                ),
                            ],
                        ),
                        # Cytoscape graph
                        html.Div(id="graph"),
                        # Shortest path
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="shortest-path-source",
                                    placeholder="Source node",
                                    style={"width": "150px"},
                                ),
                                dcc.Dropdown(
                                    id="shortest-path-target",
                                    placeholder="Target node",
                                    style={"width": "150px"},
                                ),
                                html.Button(
                                    "Find shortest path", id="shortest-path-btn"
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        # Shortest path result
                        html.Div(
                            id="shortest-path-result", style={"margin-top": "10px"}
                        ),
                        html.Div(
                            [
                                html.Button("Methodology", id="open", n_clicks=0),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(dbc.ModalTitle("Methodology")),
                                        dbc.ModalBody(
                                            html.Img(
                                                src="/assets/huy_methodology.png",
                                                style={"width": "100%"},
                                            )
                                        ),  # Replace with your image path
                                        dbc.ModalFooter(
                                            dbc.Button(
                                                "Close",
                                                id="close",
                                                className="ms-auto",
                                                n_clicks=0,
                                            )
                                        ),
                                    ],
                                    id="modal",
                                    is_open=False,
                                    size="xl",  # Extra large modal
                                    # className="modal-fullscreen"  # Custom class for full screen
                                ),
                            ]
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        # Csv table
                        html.Div(
                            id="graph-data-display",
                            style={"overflow": "scroll", "margin-bottom": "10px"},
                        ),
                        html.Button("Download CSV", id="btn-download", n_clicks=0),
                        dcc.Download(id="download-dataframe-csv"),
                    ],
                    width=4,
                ),
            ],
            style={
                "border": "1px solid #0074D9",
                "border-radius": "5px",
                "padding": "10px",
            },
        ),
        # Modal structure
        # Store to hold the graph data in CSV format
        dcc.Store(id="graph-data-store", data=[]),
    ]
)

@app.callback(
    Output("graph", "children"),
    Input("graph-data-store", "data"),
)
def update_graph_elements(data):
    elements = csv_to_graph_elements(data)
    return cytograph(elements)

# Add node button
@app.callback(
    Output("graph-data-store", "data"),
    Input("add-node-button", "n_clicks"),
    State("node-input", "value"),
    State("graph-data-store", "data"),
    # prevent_initial_call=True,
)
def add_node(n_clicks, node, data):
    if n_clicks > 0 and node:
        if node not in [entry["source"] for entry in data]:
            data.append({"source": node, "target": None, "weight": None})
    return data

# Add edge button
@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("add-edge-button", "n_clicks"),
    State("source-node-input", "value"),
    State("target-node-input", "value"),
    State("weight-input", "value"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def add_edge(n_clicks, source, target, weight, data):
    if n_clicks > 0:
        if source and target and weight is not None:
            data.append({"source": source, "target": target, "weight": weight})
    return data

# Remove node button
@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("remove-node-button", "n_clicks"),
    State("node-list-remove", "value"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def remove_node(n_clicks, nodes_to_remove, data):
    if n_clicks > 0 and nodes_to_remove:
        for node in nodes_to_remove:
            if node in [entry["source"] for entry in data]:
                data = [
                    entry
                    for entry in data
                    if entry["source"] != node and entry["target"] != node
                ]
    return data

# Remove edge button
@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("remove-edge-button", "n_clicks"),
    State("edge-list-remove", "value"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def remove_edge(n_clicks, edges_to_remove, data):
    if n_clicks > 0 and edges_to_remove:
        for edge in edges_to_remove:
            source, target = edge.split("->")
            if {"source": source, "target": target} in [
                {"source": entry["source"], "target": entry["target"]} for entry in data
            ]:
                data = [
                    entry
                    for entry in data
                    if not (entry["source"] == source and entry["target"] == target)
                ]
    return data

# Callback to update edge dropdown options
@app.callback(
    Output("source-node-input", "options"),
    Output("target-node-input", "options"),
    Output("edge-list-remove", "options"),
    Output("node-list-remove", "options"),
    Input("graph-data-store", "data"),
)
def update_dropdowns(data):
    nodes = [entry["source"] for entry in data] + [
        entry["target"] for entry in data if entry["target"]
    ]
    nodes = list(set(nodes))
    nodes.sort()

    edges = [
        f"{entry['source']}->{entry['target']}" for entry in data if entry["target"]
    ]
    node_options = [{"label": n, "value": n} for n in nodes]
    edge_options = [{"label": e, "value": e} for e in edges]
    return node_options, node_options, edge_options, node_options

# Callback to display graph data in a table
@app.callback(
    Output("graph-data-display", "children"), Input("graph-data-store", "data")
)
def display_graph_data(data):
    if not data:
        return None
    df = pd.DataFrame(data)
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        page_action="native",
        page_size=15,
        style_table={"overflowX": "auto"},
        sort_action="native",  # Enable sorting
    )

# Callback to handle CSV download
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, graph_data_store):
    if n_clicks > 0:
        df = pd.DataFrame(graph_data_store)
        return dcc.send_data_frame(df.to_csv, "graph_data.csv", index=False)

# Example
@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("example_1-btn", "n_clicks"),
    prevent_initial_call=True,
)
def example_1(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return example_1_df.to_dict("records")
    return []


@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("example_2-btn", "n_clicks"),
    prevent_initial_call=True,
)
def example_2(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return example_2_df.to_dict("records")
    return []

@app.callback(
    Output("graph-data-store", "data", allow_duplicate=True),
    Input("example_3-btn", "n_clicks"),
    prevent_initial_call=True,
)
def example_3(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return example_3_df.to_dict("records")
    return []

@app.callback(
    Output("shortest-path-source", "options"),
    Output("shortest-path-target", "options"),
    Input("graph-data-store", "data"),
)
def update_shortest_path_dropdowns(data):
    nodes = [entry["source"] for entry in data] + [
        entry["target"] for entry in data if entry["target"]
    ]
    nodes = list(set(nodes))
    nodes.sort()
    node_options = [{"label": n, "value": n} for n in nodes]
    return node_options, node_options

# Change color when shortest path sorce and target are selected
@app.callback(
    Output("graph", "children", allow_duplicate=True),
    Input("shortest-path-source", "value"),
    Input("shortest-path-target", "value"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def update_shortest_path_color(source, target, data):
    elements = csv_to_graph_elements(data, source, target)
    return cytograph(elements)

# Find shortest path
@app.callback(
    Output("shortest-path-result", "children"),
    Output("graph", "children", allow_duplicate=True),
    Input("shortest-path-btn", "n_clicks"),
    State("shortest-path-source", "value"),
    State("shortest-path-target", "value"),
    State("graph-data-store", "data"),
    prevent_initial_call=True,
)
def find_shortest_path(n_clicks, source, target, data):
    if n_clicks is not None and n_clicks > 0:
        try:
            path, weight = find_shortest_path_glpk(pd.DataFrame(data), source, target)
            message = f"Shortest Path: {path}, Total Weight: {weight}"
            graph_elelements = csv_to_graph_elements(data, source, target, path)
        except Exception as e:
            message = "No path found"
            graph_elelements = csv_to_graph_elements(data)
        return message, cytograph(graph_elelements)
    return "", cytograph(csv_to_graph_elements(data))

# Callback to toggle the modal
@app.callback(
    Output("modal", "is_open"),
    Input("open", "n_clicks"), 
    Input("close", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == "__main__":
    app.run_server(debug=False)
