# import pyomo.environ as pyo
# from pyomo.opt import SolverFactory

# def find_shortest_path_glpk(df, source_node, target_node):
#     # Initialize Pyomo model
#     m = pyo.ConcreteModel()

#     # Extract all unique points
#     all_points = list(set(df['source']).union(set(df['target'])))
#     m.setAllPoints = all_points
#     m.setPoints = [point for point in all_points if point not in [source_node, target_node]]

#     # Create sets of routes
#     routes = df[['source', 'target']].values.tolist()
#     m.setRoutes = routes

#     m.setRoutes_from = {key: [] for key in m.setAllPoints}
#     m.setRoutes_to = {key: [] for key in m.setAllPoints}
#     for route in m.setRoutes:
#         m.setRoutes_from[route[0]].append(route[1])
#         m.setRoutes_to[route[1]].append(route[0])

#     # Parameters: Distance on each route
#     m.D = {}
#     for i, row in df.iterrows():
#         m.D[row['source'], row['target']] = row['weight']

#     # Variables: Binary variable for each route
#     m.x = pyo.Var(m.setRoutes, within=pyo.Binary)

#     # Objective Function: Minimize total weight
#     m.obj = pyo.Objective(expr=sum([
#         m.x[route[0], route[1]] * m.D[route[0], route[1]]
#         for route in m.setRoutes
#     ]), sense=pyo.minimize)

#     # Constraints: Flow conservation and route selection
#     m.C1 = pyo.Constraint(expr=sum([m.x[source_node, j] for j in m.setRoutes_from[source_node]]) == 1)
#     m.C2 = pyo.Constraint(expr=sum([m.x[i, target_node] for i in m.setRoutes_to[target_node]]) == 1)
#     m.C3 = pyo.ConstraintList()
#     for i in m.setPoints:
#         m.C3.add(sum([m.x[i, j] for j in m.setRoutes_from[i]]) == sum([m.x[j, i] for j in m.setRoutes_to[i]]))

#     # Solve the model using GLPK
#     opt = SolverFactory('glpk')
#     m.results = opt.solve(m)

#     # Extract the solution
#     path = []
#     total_weight = pyo.value(m.obj)
#     for route in m.setRoutes:
#         if pyo.value(m.x[route[0], route[1]]) >= 0.9:
#             path.append((route[0], route[1]))

#     return path, total_weight

import pandas as pd
import numpy as np
from ortools.sat.python import cp_model

def find_shortest_path_ortools(df, source_node, target_node):
    # Initialize OR-Tools CP-SAT model
    model = cp_model.CpModel()

    # Extract all unique points
    all_points = list(set(df['source']).union(set(df['target'])))
    n_points = len(all_points)
    n_paths = len(df)

    # Decision variables: x[p] is 1 if path p is used, 0 otherwise
    x = [model.NewIntVar(0, 1, f'x[{p}]') for p in range(n_paths)]

    # Objective function: Minimize the total distance
    model.Minimize(sum(x[p] * df['weight'].iloc[p] for p in range(n_paths)))

    # Constraints: Ensure the source and target nodes have exactly one path leaving/entering
    model.Add(sum(x[p] for p in range(n_paths) if df['source'].iloc[p] == source_node) == 1)
    model.Add(sum(x[p] for p in range(n_paths) if df['target'].iloc[p] == target_node) == 1)

    # Constraints: Flow conservation for all middle nodes
    middle_points = [point for point in all_points if point not in [source_node, target_node]]
    for node in middle_points:
        sum_in = sum(x[p] for p in range(n_paths) if df['target'].iloc[p] == node)
        sum_out = sum(x[p] for p in range(n_paths) if df['source'].iloc[p] == node)
        model.Add(sum_in == sum_out)

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Extract and return the solution
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        path = []
        total_weight = solver.ObjectiveValue()
        for p in range(n_paths):
            if solver.Value(x[p]) == 1:
                path.append((df['source'].iloc[p], df['target'].iloc[p]))

        return path, total_weight
    else:
        print(f'Solution Status: {solver.StatusName(status)}')
        return None, None

# # Example usage:
# df = pd.DataFrame({
#     'source': ['A', 'A', 'B', 'B', 'C', 'C', 'D'],
#     'target': ['B', 'C', 'A', 'D', 'B', 'E', 'E'],
#     'weight': [10, 3, 20, 5, 2, 15, 11]
# })
# path, weight = find_shortest_path_ortools(df, source_node="A", target_node="E")
# print("Shortest Path:", path)
# print("Total Weight:", weight)