import pyomo.environ as pyo
from pyomo.opt import SolverFactory

def find_shortest_path_glpk(df, source_node, target_node):
    # Initialize Pyomo model
    m = pyo.ConcreteModel()

    # Extract all unique points
    all_points = list(set(df['source']).union(set(df['target'])))
    m.setAllPoints = all_points
    m.setPoints = [point for point in all_points if point not in [source_node, target_node]]

    # Create sets of routes
    routes = df[['source', 'target']].values.tolist()
    m.setRoutes = routes

    m.setRoutes_from = {key: [] for key in m.setAllPoints}
    m.setRoutes_to = {key: [] for key in m.setAllPoints}
    for route in m.setRoutes:
        m.setRoutes_from[route[0]].append(route[1])
        m.setRoutes_to[route[1]].append(route[0])

    # Parameters: Distance on each route
    m.D = {}
    for i, row in df.iterrows():
        m.D[row['source'], row['target']] = row['weight']

    # Variables: Binary variable for each route
    m.x = pyo.Var(m.setRoutes, within=pyo.Binary)

    # Objective Function: Minimize total weight
    m.obj = pyo.Objective(expr=sum([
        m.x[route[0], route[1]] * m.D[route[0], route[1]]
        for route in m.setRoutes
    ]), sense=pyo.minimize)

    # Constraints: Flow conservation and route selection
    m.C1 = pyo.Constraint(expr=sum([m.x[source_node, j] for j in m.setRoutes_from[source_node]]) == 1)
    m.C2 = pyo.Constraint(expr=sum([m.x[i, target_node] for i in m.setRoutes_to[target_node]]) == 1)
    m.C3 = pyo.ConstraintList()
    for i in m.setPoints:
        m.C3.add(sum([m.x[i, j] for j in m.setRoutes_from[i]]) == sum([m.x[j, i] for j in m.setRoutes_to[i]]))

    # Solve the model using GLPK
    opt = SolverFactory('glpk')
    m.results = opt.solve(m)

    # Extract the solution
    path = []
    total_weight = pyo.value(m.obj)
    for route in m.setRoutes:
        if pyo.value(m.x[route[0], route[1]]) >= 0.9:
            path.append((route[0], route[1]))

    return path, total_weight

# Example usage (assuming df is the loaded DataFrame):
# path, weight = find_shortest_path_glpk(df, source_node="A", target_node="B")
# print("Shortest Path:", path)
# print("Total Weight:", weight)